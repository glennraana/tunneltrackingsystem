import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import cors from 'cors';
import express, { Request, Response } from 'express';

admin.initializeApp();

const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

const db = admin.firestore();

// API endpoint for MCP server/Rajant parser to log node data
app.post('/api/log-position', async (req: Request, res: Response): Promise<void> => {
  try {
    const { mac_address, node_id, timestamp, signal_strength } = req.body;

    // Validate required fields
    if (!mac_address || !node_id || !timestamp) {
      res.status(400).json({
        error: 'Missing required fields: mac_address, node_id, timestamp'
      });
      return;
    }

    // Check if MAC address is registered
    const userQuery = await db.collection('users')
      .where('mac_address', '==', mac_address)
      .limit(1)
      .get();

    if (!userQuery.empty) {
      // User is registered - log position
      const positionData = {
        mac_address,
        node_id,
        timestamp: admin.firestore.Timestamp.fromDate(new Date(timestamp)),
        signal_strength: signal_strength || null,
        logged_at: admin.firestore.FieldValue.serverTimestamp()
      };

      await db.collection('positions').add(positionData);

      // Update node status
      await db.collection('nodes').doc(node_id).set({
        last_seen: admin.firestore.FieldValue.serverTimestamp(),
        active_status: true
      }, { merge: true });

      res.status(200).json({
        success: true,
        message: 'Position logged successfully',
        registered_user: true
      });
    } else {
      // MAC not registered - log as unregistered
      const unregisteredData = {
        mac_address,
        node_id,
        timestamp: admin.firestore.Timestamp.fromDate(new Date(timestamp)),
        signal_strength: signal_strength || null,
        logged_at: admin.firestore.FieldValue.serverTimestamp()
      };

      await db.collection('unregistered_logs').add(unregisteredData);

      res.status(200).json({
        success: true,
        message: 'Unregistered MAC logged',
        registered_user: false,
        warning: 'Unauthorized access detected'
      });
    }
  } catch (error) {
    console.error('Error logging position:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get live tunnel status
app.get('/api/tunnel-status', async (req: Request, res: Response) => {
  try {
    const now = new Date();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);

    // Get active users (users seen in last 5 minutes)
    const recentPositions = await db.collection('positions')
      .where('timestamp', '>=', admin.firestore.Timestamp.fromDate(fiveMinutesAgo))
      .orderBy('timestamp', 'desc')
      .get();

    // Group positions by MAC address to get latest position for each user
    const latestPositions = new Map();
    recentPositions.forEach(doc => {
      const data = doc.data();
      const macAddress = data.mac_address;
      
      if (!latestPositions.has(macAddress)) {
        latestPositions.set(macAddress, {
          mac_address: macAddress,
          node_id: data.node_id,
          timestamp: data.timestamp,
          signal_strength: data.signal_strength
        });
      }
    });

    // Get user details for registered MAC addresses
    const users = await db.collection('users').get();
    const userMap = new Map();
    users.forEach(doc => {
      const userData = doc.data();
      userMap.set(userData.mac_address, {
        id: doc.id,
        name: userData.name,
        mac_address: userData.mac_address,
        registered_at: userData.registered_at
      });
    });

    // Create active users list with details
    const activeUsers = Array.from(latestPositions.values())
      .filter(pos => userMap.has(pos.mac_address))
      .map(pos => {
        const user = userMap.get(pos.mac_address);
        // Map node IDs to readable names
        const nodeNameMap: { [key: string]: string } = {
          'rajant_1': 'kjøkken',
          'rajant_2': 'Gang',
          'entrance_01': 'Hovedinngang',
          'section_a1': 'Seksjon A1',
          'exit_01': 'Utgang Nord'
        };
        const readableLocation = nodeNameMap[pos.node_id] || pos.node_id;
        
        return {
          id: user.id,
          name: user.name,
          mac_address: pos.mac_address,
          current_location: readableLocation,
          last_seen: pos.timestamp,
          signal_strength: pos.signal_strength
        };
      });

    // Get total registered users today
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    
    const todayRegistrations = await db.collection('users')
      .where('registered_at', '>=', admin.firestore.Timestamp.fromDate(todayStart))
      .get();

    // Get active nodes
    const activeNodes = await db.collection('nodes')
      .where('active_status', '==', true)
      .get();

    const totalNodes = await db.collection('nodes').get();

    // Get recent unregistered attempts with details
    const recentUnregistered = await db.collection('unregistered_logs')
      .where('timestamp', '>=', admin.firestore.Timestamp.fromDate(fiveMinutesAgo))
      .orderBy('timestamp', 'desc')
      .get();

    // Group unauthorized devices by MAC to avoid duplicates
    const unauthorizedDevices = new Map();
    recentUnregistered.forEach(doc => {
      const data = doc.data();
      const macAddress = data.mac_address;
      
      if (!unauthorizedDevices.has(macAddress)) {
        // Map node IDs to readable names
        const nodeNameMap: { [key: string]: string } = {
          'rajant_1': 'kjøkken',
          'rajant_2': 'Gang',
          'entrance_01': 'Hovedinngang',
          'section_a1': 'Seksjon A1',
          'exit_01': 'Utgang Nord'
        };
        const readableNodeName = nodeNameMap[data.node_id] || data.node_id;
        
        unauthorizedDevices.set(macAddress, {
          mac_address: macAddress,
          node_name: readableNodeName,
          detected_at: data.timestamp,
          signal_strength: data.signal_strength
        });
      }
    });

    res.status(200).json({
      active_users_count: activeUsers.length,
      active_users: Array.from(activeUsers.values()),
      active_nodes_count: activeNodes.size,
      total_nodes_count: totalNodes.size,
      registered_today_count: todayRegistrations.size,
      unregistered_attempts: unauthorizedDevices.size,
      unauthorized_devices: Array.from(unauthorizedDevices.values()),
      last_updated: admin.firestore.FieldValue.serverTimestamp()
    });
  } catch (error) {
    console.error('Error getting tunnel status:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get current positions of all users
app.get('/api/current-positions', async (req: Request, res: Response) => {
  try {
    // Get the latest position for each MAC address
    const positions = await db.collection('positions')
      .orderBy('timestamp', 'desc')
      .get();

    const latestPositions = new Map();
    
    positions.forEach(doc => {
      const data = doc.data();
      const macAddress = data.mac_address;
      
      if (!latestPositions.has(macAddress)) {
        latestPositions.set(macAddress, {
          mac_address: macAddress,
          node_id: data.node_id,
          timestamp: data.timestamp,
          signal_strength: data.signal_strength
        });
      }
    });

    // Get user names for registered MAC addresses
    const users = await db.collection('users').get();
    const userMap = new Map();
    users.forEach(doc => {
      const userData = doc.data();
      userMap.set(userData.mac_address, userData.name);
    });

    // Combine position data with user names
    const result = Array.from(latestPositions.values()).map(position => ({
      ...position,
      user_name: userMap.get(position.mac_address) || 'Unknown'
    }));

    res.status(200).json({
      positions: result,
      count: result.length
    });
  } catch (error) {
    console.error('Error getting current positions:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Admin endpoint to create/update nodes
app.post('/api/admin/nodes', async (req: Request, res: Response): Promise<void> => {
  try {
    const { node_id, name, location, active_status = true } = req.body;

    if (!node_id || !name) {
      res.status(400).json({
        error: 'Missing required fields: node_id, name'
      });
      return;
    }

    const nodeData = {
      node_id,
      name,
      location: location || { x: 0, y: 0 },
      active_status,
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      updated_at: admin.firestore.FieldValue.serverTimestamp()
    };

    await db.collection('nodes').doc(node_id).set(nodeData, { merge: true });

    res.status(200).json({
      success: true,
      message: 'Node updated successfully',
      node_id
    });
  } catch (error) {
    console.error('Error updating node:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all nodes
app.get('/api/nodes', async (req: Request, res: Response) => {
  try {
    const nodes = await db.collection('nodes').get();
    const nodeList: any[] = [];

    nodes.forEach(doc => {
      nodeList.push({
        id: doc.id,
        ...doc.data()
      });
    });

    res.status(200).json({
      nodes: nodeList,
      count: nodeList.length
    });
  } catch (error) {
    console.error('Error getting nodes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all users
app.get('/api/users', async (req: Request, res: Response) => {
  try {
    const users = await db.collection('users').get();
    const userList: any[] = [];

    users.forEach(doc => {
      userList.push({
        id: doc.id,
        ...doc.data()
      });
    });

    res.status(200).json({
      users: userList,
      count: userList.length
    });
  } catch (error) {
    console.error('Error getting users:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create or update user
app.post('/api/users', async (req: Request, res: Response): Promise<void> => {
  try {
    const { name, mac_address, location_description } = req.body;

    if (!name || !mac_address) {
      res.status(400).json({
        error: 'Missing required fields: name, mac_address'
      });
      return;
    }

    const userData = {
      name,
      mac_address,
      location_description: location_description || '',
      registered_at: admin.firestore.FieldValue.serverTimestamp(),
      updated_at: admin.firestore.FieldValue.serverTimestamp(),
      active_status: true
    };

    // Check if user with this MAC already exists
    const existingUser = await db.collection('users')
      .where('mac_address', '==', mac_address)
      .limit(1)
      .get();

    if (!existingUser.empty) {
      // Update existing user
      const docId = existingUser.docs[0].id;
      await db.collection('users').doc(docId).update({
        ...userData,
        updated_at: admin.firestore.FieldValue.serverTimestamp()
      });
      
      res.status(200).json({
        success: true,
        message: 'User updated successfully',
        user_id: docId
      });
    } else {
      // Create new user
      const docRef = await db.collection('users').add(userData);
      
      res.status(201).json({
        success: true,
        message: 'User created successfully',
        user_id: docRef.id
      });
    }
  } catch (error) {
    console.error('Error creating/updating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get unauthorized devices (recent unregistered attempts)
app.get('/api/unauthorized-devices', async (req: Request, res: Response) => {
  try {
    const fiveMinutesAgo = new Date();
    fiveMinutesAgo.setMinutes(fiveMinutesAgo.getMinutes() - 5);

    const unauthorizedLogs = await db.collection('unregistered_logs')
      .where('timestamp', '>=', admin.firestore.Timestamp.fromDate(fiveMinutesAgo))
      .orderBy('timestamp', 'desc')
      .get();

    const deviceList: any[] = [];
    const seenMacs = new Set();

    unauthorizedLogs.forEach(doc => {
      const data = doc.data();
      if (!seenMacs.has(data.mac_address)) {
        seenMacs.add(data.mac_address);
        deviceList.push({
          mac_address: data.mac_address,
          node_id: data.node_id,
          detected_at: data.timestamp,
          signal_strength: data.signal_strength
        });
      }
    });

    res.status(200).json({
      unauthorized_devices: deviceList,
      count: deviceList.length
    });
  } catch (error) {
    console.error('Error getting unauthorized devices:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Log unauthorized access
app.post('/api/log-unauthorized', async (req: Request, res: Response): Promise<void> => {
  try {
    const { mac_address, node_id, timestamp, signal_strength, metadata } = req.body;

    if (!mac_address || !node_id) {
      res.status(400).json({
        error: 'Missing required fields: mac_address, node_id'
      });
      return;
    }

    const unauthorizedData = {
      mac_address,
      node_id,
      timestamp: timestamp || new Date().toISOString(),
      signal_strength: signal_strength || -50,
      metadata: metadata || {},
      created_at: admin.firestore.FieldValue.serverTimestamp()
    };

    await db.collection('unregistered_logs').add(unauthorizedData);

    res.status(200).json({
      success: true,
      message: 'Unauthorized access logged successfully'
    });
  } catch (error) {
    console.error('Error logging unauthorized access:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'tunnel-tracking-api'
  });
});

// Export the API as a Firebase Function
export const api = functions.https.onRequest(app);

// Cleanup old data function (runs daily)
export const cleanupOldData = functions.pubsub.schedule('0 2 * * *')
  .timeZone('Europe/Oslo')
  .onRun(async (context) => {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    try {
      // Delete old positions
      const oldPositions = await db.collection('positions')
        .where('timestamp', '<=', admin.firestore.Timestamp.fromDate(thirtyDaysAgo))
        .get();

      const batch = db.batch();
      oldPositions.forEach(doc => {
        batch.delete(doc.ref);
      });

      await batch.commit();

      console.log(`Cleaned up ${oldPositions.size} old position records`);
    } catch (error) {
      console.error('Error during cleanup:', error);
    }
  }); 