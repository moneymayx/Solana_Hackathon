#!/usr/bin/env python3
"""
Billions Personality Editor
=========================

Interactive tool for customizing and testing Billions's personality.
This script allows you to:
- View different personality components
- Edit specific aspects of Billions's character
- Test personality changes with sample conversations
- Save and load personality configurations
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.personality import BillionsPersonality
from src.ai_agent import BillionsAgent

class PersonalityEditor:
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the AI agent if API key is available"""
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.agent = BillionsAgent()
                print("✅ AI Agent initialized successfully!")
            except Exception as e:
                print(f"⚠️  Could not initialize AI agent: {e}")
                print("   You can still edit personality components.")
        else:
            print("⚠️  ANTHROPIC_API_KEY not found. AI testing disabled.")
            print("   You can still edit personality components.")
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🤖 BENITA PERSONALITY EDITOR")
        print("="*60)
        print("1. View personality components")
        print("2. Test current personality")
        print("3. Edit personality components")
        print("4. View conversation examples")
        print("5. Reset to default personality")
        print("6. Save personality to file")
        print("7. Load personality from file")
        print("8. Exit")
        print("-"*60)
    
    def view_personality_components(self):
        """Display all personality components"""
        components = {
            "1": ("Core Identity", BillionsPersonality.get_core_identity()),
            "2": ("Personality Traits", BillionsPersonality.get_personality_traits()),
            "3": ("Core Directive", BillionsPersonality.get_core_directive()),
            "4": ("Communication Style", BillionsPersonality.get_communication_style()),
            "5": ("Security Awareness", BillionsPersonality.get_security_awareness()),
            "6": ("Response Guidelines", BillionsPersonality.get_response_guidelines()),
            "7": ("Conversation Examples", BillionsPersonality.get_conversation_examples()),
            "8": ("Complete Personality", BillionsPersonality.get_complete_personality())
        }
        
        print("\n📋 PERSONALITY COMPONENTS:")
        for key, (name, _) in components.items():
            print(f"{key}. {name}")
        print("9. Back to main menu")
        
        choice = input("\nSelect component to view: ").strip()
        
        if choice in components:
            name, content = components[choice]
            print(f"\n{'='*60}")
            print(f"📖 {name.upper()}")
            print(f"{'='*60}")
            print(content)
            input("\nPress Enter to continue...")
        elif choice == "9":
            return
        else:
            print("❌ Invalid choice!")
    
    def test_personality(self):
        """Test the current personality with sample conversations"""
        if not self.agent:
            print("❌ AI agent not available. Please set ANTHROPIC_API_KEY.")
            return
        
        print("\n🧪 PERSONALITY TESTING")
        print("="*40)
        print("Type 'quit' to exit testing mode")
        print("Type 'reset' to clear conversation history")
        print("-"*40)
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'reset':
                self.agent.reset_conversation()
                print("🔄 Conversation history cleared!")
                continue
            elif user_input:
                try:
                    response = self.agent.chat(user_input)
                    print(f"\nBillions: {response}")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    def edit_personality_component(self):
        """Edit a specific personality component"""
        components = {
            "1": "Core Identity",
            "2": "Personality Traits", 
            "3": "Core Directive",
            "4": "Communication Style",
            "5": "Security Awareness",
            "6": "Response Guidelines",
            "7": "Conversation Examples"
        }
        
        print("\n✏️  EDIT PERSONALITY COMPONENT:")
        for key, name in components.items():
            print(f"{key}. {name}")
        print("8. Back to main menu")
        
        choice = input("\nSelect component to edit: ").strip()
        
        if choice in components:
            component_name = components[choice]
            print(f"\n📝 Editing: {component_name}")
            print("="*50)
            
            # Get current content
            if choice == "1":
                current_content = BillionsPersonality.get_core_identity()
            elif choice == "2":
                current_content = BillionsPersonality.get_personality_traits()
            elif choice == "3":
                current_content = BillionsPersonality.get_core_directive()
            elif choice == "4":
                current_content = BillionsPersonality.get_communication_style()
            elif choice == "5":
                current_content = BillionsPersonality.get_security_awareness()
            elif choice == "6":
                current_content = BillionsPersonality.get_response_guidelines()
            elif choice == "7":
                current_content = BillionsPersonality.get_conversation_examples()
            
            print("Current content:")
            print("-"*30)
            print(current_content)
            print("-"*30)
            
            print("\n⚠️  Note: To edit this component, you'll need to modify the")
            print("   BillionsPersonality class in src/personality.py directly.")
            print("   This is by design to maintain code quality and version control.")
            
            input("\nPress Enter to continue...")
        elif choice == "8":
            return
        else:
            print("❌ Invalid choice!")
    
    def view_conversation_examples(self):
        """Display conversation examples"""
        examples = BillionsPersonality.get_conversation_examples()
        print("\n💬 CONVERSATION EXAMPLES")
        print("="*50)
        print(examples)
        input("\nPress Enter to continue...")
    
    def reset_personality(self):
        """Reset to default personality"""
        print("\n🔄 RESET TO DEFAULT PERSONALITY")
        print("="*40)
        confirm = input("Are you sure you want to reset to default? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            # Reinitialize the agent with default personality
            if self.agent:
                self.agent.personality = BillionsPersonality.get_complete_personality()
            print("✅ Personality reset to default!")
        else:
            print("❌ Reset cancelled.")
    
    def save_personality(self):
        """Save current personality to a file"""
        filename = input("\nEnter filename to save personality (e.g., 'benita_v2.txt'): ").strip()
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(BillionsPersonality.get_complete_personality())
                print(f"✅ Personality saved to {filename}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")
    
    def load_personality(self):
        """Load personality from a file"""
        filename = input("\nEnter filename to load personality from: ").strip()
        
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                
                if self.agent:
                    self.agent.update_personality(content)
                    print(f"✅ Personality loaded from {filename}")
                    print("⚠️  Note: This is a temporary change. To make it permanent,")
                    print("   you'll need to update the BillionsPersonality class.")
                else:
                    print(f"✅ File loaded successfully!")
                    print("   Content preview:")
                    print("-"*30)
                    print(content[:500] + "..." if len(content) > 500 else content)
            except Exception as e:
                print(f"❌ Error loading file: {e}")
        else:
            print("❌ File not found!")
    
    def run(self):
        """Main application loop"""
        print("🤖 Welcome to the Billions Personality Editor!")
        
        while True:
            self.show_menu()
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                self.view_personality_components()
            elif choice == "2":
                self.test_personality()
            elif choice == "3":
                self.edit_personality_component()
            elif choice == "4":
                self.view_conversation_examples()
            elif choice == "5":
                self.reset_personality()
            elif choice == "6":
                self.save_personality()
            elif choice == "7":
                self.load_personality()
            elif choice == "8":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please select 1-8.")

def main():
    """Main entry point"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    editor = PersonalityEditor()
    editor.run()

if __name__ == "__main__":
    main()
