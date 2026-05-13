#!/usr/bin/env python
"""
Test the Terraform parser with sample files
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.terraform_parser import TerraformParser

if __name__ == "__main__":
    parser = TerraformParser()
    
    # Test with sample-terraform directory
    sample_dir = Path(__file__).parent.parent.parent / "sample-terraform"
    
    if sample_dir.exists():
        print(f"📁 Parsing {sample_dir}...")
        result = parser.parse_repository(str(sample_dir))
        
        print(f"\n✅ Parse Result:")
        print(f"  Status: {result['status']}")
        print(f"  Files: {len(result['files'])}")
        print(f"  Modules: {len(result['modules'])}")
        print(f"  Resources: {len(result['resources'])}")
        print(f"  Variables: {len(result['variables'])}")
        print(f"  Outputs: {len(result['outputs'])}")
        print(f"  Providers: {len(result['providers'])}")
        print(f"  References: {len(result['references'])}")
        
        if result['errors']:
            print(f"\n❌ Errors:")
            for error in result['errors']:
                print(f"  - {error}")
    else:
        print(f"❌ Sample directory not found: {sample_dir}")
        sys.exit(1)
