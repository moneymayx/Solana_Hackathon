#!/bin/bash

# Banner Images Update Script
# This script helps you easily update banner images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Image directory
IMAGE_DIR="public/images"

# Available slides (using functions instead of associative arrays for compatibility)
get_slide_filename() {
    case $1 in
        1) echo "claude-ai.svg" ;;
        2) echo "mobile-app.svg" ;;
        3) echo "referral-bonus.svg" ;;
        4) echo "gpt-4.svg" ;;
        5) echo "gemini-ai.svg" ;;
        6) echo "llama-ai.svg" ;;
        *) echo "" ;;
    esac
}

get_slide_title() {
    case $1 in
        1) echo "Claude Challenge" ;;
        2) echo "Download App" ;;
        3) echo "Referral Program" ;;
        4) echo "GPT-4 Bounty" ;;
        5) echo "Gemini Quest" ;;
        6) echo "Llama Legend" ;;
        *) echo "" ;;
    esac
}

is_valid_slide() {
    [[ "$1" =~ ^[1-6]$ ]]
}

echo -e "${BLUE}🎨 Banner Images Update Script${NC}"
echo "=================================="
echo ""

# Function to show available slides
show_slides() {
    echo -e "${YELLOW}Available slides to update:${NC}"
    echo ""
    for i in {1..6}; do
        local filename=$(get_slide_filename $i)
        local title=$(get_slide_title $i)
        echo "  $i) $title ($filename)"
    done
    echo ""
}

# Function to update an image
update_image() {
    local slide_num=$1
    local new_image_path=$2
    
    if ! is_valid_slide "$slide_num"; then
        echo -e "${RED}❌ Invalid slide number: $slide_num${NC}"
        return 1
    fi
    
    local filename=$(get_slide_filename $slide_num)
    local title=$(get_slide_title $slide_num)
    local target_path="$IMAGE_DIR/$filename"
    
    if [[ ! -f "$new_image_path" ]]; then
        echo -e "${RED}❌ Source image not found: $new_image_path${NC}"
        return 1
    fi
    
    # Create backup
    if [[ -f "$target_path" ]]; then
        cp "$target_path" "$target_path.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📦 Created backup: $target_path.backup.$(date +%Y%m%d_%H%M%S)${NC}"
    fi
    
    # Copy new image
    cp "$new_image_path" "$target_path"
    echo -e "${GREEN}✅ Updated $title ($filename)${NC}"
}

# Function to restore from backup
restore_backup() {
    local slide_num=$1
    
    if ! is_valid_slide "$slide_num"; then
        echo -e "${RED}❌ Invalid slide number: $slide_num${NC}"
        return 1
    fi
    
    local filename=$(get_slide_filename $slide_num)
    local title=$(get_slide_title $slide_num)
    local target_path="$IMAGE_DIR/$filename"
    
    # Find latest backup
    local latest_backup=$(ls -t "$target_path.backup."* 2>/dev/null | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        echo -e "${RED}❌ No backup found for $title${NC}"
        return 1
    fi
    
    cp "$latest_backup" "$target_path"
    echo -e "${GREEN}✅ Restored $title from backup: $(basename "$latest_backup")${NC}"
}

# Function to list backups
list_backups() {
    echo -e "${YELLOW}Available backups:${NC}"
    echo ""
    for i in {1..6}; do
        local filename=$(get_slide_filename $i)
        local title=$(get_slide_title $i)
        local target_path="$IMAGE_DIR/$filename"
        local backups=$(ls -t "$target_path.backup."* 2>/dev/null || true)
        
        if [[ -n "$backups" ]]; then
            echo "  $title ($filename):"
            echo "$backups" | head -3 | sed 's/^/    /'
            if [[ $(echo "$backups" | wc -l) -gt 3 ]]; then
                echo "    ... and $(( $(echo "$backups" | wc -l) - 3 )) more"
            fi
            echo ""
        fi
    done
}

# Main script logic
case "${1:-help}" in
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  update <slide_number> <image_path>  Update a specific slide"
        echo "  restore <slide_number>              Restore from latest backup"
        echo "  list                                Show available slides"
        echo "  backups                             List available backups"
        echo "  interactive                         Interactive mode"
        echo ""
        show_slides
        ;;
    
    "update")
        if [[ $# -ne 3 ]]; then
            echo -e "${RED}❌ Usage: $0 update <slide_number> <image_path>${NC}"
            exit 1
        fi
        update_image "$2" "$3"
        ;;
    
    "restore")
        if [[ $# -ne 2 ]]; then
            echo -e "${RED}❌ Usage: $0 restore <slide_number>${NC}"
            exit 1
        fi
        restore_backup "$2"
        ;;
    
    "list")
        show_slides
        ;;
    
    "backups")
        list_backups
        ;;
    
    "interactive")
        echo -e "${BLUE}🎯 Interactive Mode${NC}"
        echo "=================="
        echo ""
        
        while true; do
            show_slides
            echo "Options:"
            echo "  u) Update an image"
            echo "  r) Restore from backup"
            echo "  b) List backups"
            echo "  q) Quit"
            echo ""
            read -p "Choose an option: " choice
            
            case $choice in
                "u"|"update")
                    read -p "Enter slide number (1-6): " slide_num
                    read -p "Enter path to new image: " image_path
                    update_image "$slide_num" "$image_path"
                    ;;
                "r"|"restore")
                    read -p "Enter slide number to restore (1-6): " slide_num
                    restore_backup "$slide_num"
                    ;;
                "b"|"backups")
                    list_backups
                    ;;
                "q"|"quit")
                    echo -e "${GREEN}👋 Goodbye!${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}❌ Invalid option${NC}"
                    ;;
            esac
            echo ""
        done
        ;;
    
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Done! Don't forget to refresh your browser to see changes.${NC}"
