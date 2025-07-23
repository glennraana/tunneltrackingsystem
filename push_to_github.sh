#!/bin/bash
# Script to push Tunnel Tracking System to GitHub
# Run this from your laptop/desktop with git access

set -e

echo "🚀 Pushing Tunnel Tracking System to GitHub"
echo "==========================================="

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
   echo "❌ Please run this from the workspace root directory"
   echo "   (where README.md is located)"
   exit 1
fi

# Set your GitHub repository URL here
REPO_URL="https://github.com/glennraana/tunneltrackingsystem.git"
echo "📍 Repository: $REPO_URL"

# Check if git is initialized
if [[ ! -d ".git" ]]; then
    echo "🔧 Initializing git repository..."
    git init
    git remote add origin $REPO_URL
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📁 Adding files to git..."
git add README.md
git add .gitignore
git add GITHUB_SETUP.md
git add scripts/
git add docs/
git add .firebaserc
git add firebase.json
git add firestore.indexes.json
git add firestore.rules
git add admin_dashboard/
git add mobile_app/
git add cloud_functions/
git add firebase_config/

# Check what's staged
echo "📋 Files to be committed:"
git status --short

# Create commit
echo "💾 Creating commit..."
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit - files might already be up to date"
    echo "🔄 Force adding and committing..."
    git add -A
fi

git commit -m "Complete Tunnel Tracking System

✅ Raspberry Pi integration scripts (Rajant API)
✅ Flutter mobile app for worker registration
✅ Flutter admin dashboard (web)
✅ Firebase Cloud Functions API
✅ Firestore database with security rules
✅ Complete documentation and setup guides

🎯 Ready for production deployment! 🚀" || echo "⚠️  Commit failed - might be no changes"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ SUCCESS! Repository pushed to GitHub!"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Go to your Pi and run:"
echo "   git clone $REPO_URL"
echo "   cd tunneltrackingsystem/scripts"
echo "   chmod +x quick_start.sh"
echo "   ./quick_start.sh"
echo ""
echo "2. Configure Rajant nodes in config.yaml"
echo "3. Test and deploy!"
echo ""
echo "📱 Admin dashboard: https://tunnel-tracking-system.web.app" 
