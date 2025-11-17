#!/bin/bash
# Git deployment helper script

echo "=========================================="
echo "Teveclub Git Deployment Helper"
echo "=========================================="
echo ""

echo "Select operation:"
echo "1. Pull latest changes"
echo "2. Fix merge conflicts"
echo "3. Fix aborted git operations"
echo "4. Force pull (discard local changes)"
echo "5. Git status"
echo ""
read -p "Choose option (1-5): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "Pulling latest changes..."
        
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            echo "You have uncommitted changes"
            read -p "Stash changes? (y/n): " STASH
            if [ "$STASH" = "y" ]; then
                git stash
            fi
        fi
        
        if git pull; then
            echo "Pull successful"
            read -p "Restart service? (y/n): " RESTART
            if [ "$RESTART" = "y" ]; then
                sudo systemctl restart teveclub
            fi
        fi
        ;;
        
    2)
        echo ""
        if git status | grep -q "unmerged"; then
            echo "Conflicts detected:"
            git diff --name-only --diff-filter=U
            echo ""
            echo "1. Abort merge"
            echo "2. Force pull"
            read -p "Choose: " OPT
            
            if [ "$OPT" = "1" ]; then
                git merge --abort
            elif [ "$OPT" = "2" ]; then
                git reset --hard HEAD
                git pull --force
            fi
        else
            echo "No conflicts"
        fi
        ;;
        
    3)
        echo ""
        if [ -f .git/MERGE_HEAD ]; then
            git merge --abort
            echo "Merge aborted"
        elif [ -d .git/rebase-merge ]; then
            git rebase --abort
            echo "Rebase aborted"
        else
            echo "No aborted operations"
        fi
        ;;
        
    4)
        echo ""
        echo "WARNING: Discard ALL local changes!"
        read -p "Sure? (yes/no): " CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            git fetch origin
            git reset --hard origin/main
            echo "Force pull complete"
        fi
        ;;
        
    5)
        git status
        echo ""
        git log --oneline -5
        ;;
esac
