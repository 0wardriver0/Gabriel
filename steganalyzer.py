#!/usr/bin/env python3

import os
import sys
from PIL import Image
import numpy as np
import argparse
from pathlib import Path
import concurrent.futures
from datetime import datetime

def analyze_image(image_path):
    """
    Analyze a single image for potential steganography.
    Returns a dictionary with analysis results.
    """
    try:
        # Load the image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        results = {
            'filename': os.path.basename(image_path),
            'size': os.path.getsize(image_path),
            'dimensions': img.size,
            'format': img.format,
            'mode': img.mode,
            'potential_steganography': False,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'warnings': []
        }
        
        # Check for LSB steganography by analyzing bit patterns
        if len(img_array.shape) == 3:  # Color image
            for channel in range(3):
                channel_data = img_array[:, :, channel]
                
                # Check for unusual patterns in LSB
                lsb = channel_data & 1
                if np.mean(lsb) > 0.6 or np.mean(lsb) < 0.4:  # Unusual LSB distribution
                    results['warnings'].append(f"Unusual LSB pattern in channel {channel}")
                    results['potential_steganography'] = True
                
                # Check for unusual pixel value distribution
                if np.std(channel_data) < 10:  # Unusually low variation
                    results['warnings'].append(f"Unusual pixel distribution in channel {channel}")
                    results['potential_steganography'] = True
                
                # Check for unusual entropy
                hist = np.histogram(channel_data, bins=256, range=(0, 256))[0]
                hist = hist[hist > 0]
                entropy = -np.sum((hist/len(channel_data.flatten())) * np.log2(hist/len(channel_data.flatten())))
                if entropy < 7.0:  # Unusually low entropy
                    results['warnings'].append(f"Low entropy in channel {channel}")
                    results['potential_steganography'] = True
        
        return results
    
    except Exception as e:
        return {
            'filename': os.path.basename(image_path),
            'error': str(e),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def analyze_directory(directory_path, output_file=None):
    """
    Analyze all images in a directory and its subdirectories.
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    results = []
    
    # Find all image files
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(directory_path).rglob(f'*{ext}'))
    
    print(f"Found {len(image_files)} images to analyze...")
    
    # Analyze images in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(analyze_image, image_files))
    
    # Print results
    print("\nAnalysis Results:")
    print("=" * 80)
    
    suspicious_files = []
    for result in results:
        if 'error' in result:
            print(f"\nError analyzing {result['filename']}: {result['error']}")
            continue
            
        print(f"\nFile: {result['filename']}")
        print(f"Size: {result['size']} bytes")
        print(f"Dimensions: {result['dimensions']}")
        print(f"Format: {result['format']}")
        print(f"Mode: {result['mode']}")
        
        if result['potential_steganography']:
            suspicious_files.append(result['filename'])
            print("⚠️  POTENTIAL STEGANOGRAPHY DETECTED!")
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        else:
            print("✓ No obvious signs of steganography")
    
    # Save results to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write("Steganography Analysis Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Analysis performed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in results:
                if 'error' in result:
                    f.write(f"\nError analyzing {result['filename']}: {result['error']}\n")
                    continue
                    
                f.write(f"\nFile: {result['filename']}\n")
                f.write(f"Size: {result['size']} bytes\n")
                f.write(f"Dimensions: {result['dimensions']}\n")
                f.write(f"Format: {result['format']}\n")
                f.write(f"Mode: {result['mode']}\n")
                
                if result['potential_steganography']:
                    f.write("⚠️  POTENTIAL STEGANOGRAPHY DETECTED!\n")
                    f.write("Warnings:\n")
                    for warning in result['warnings']:
                        f.write(f"  - {warning}\n")
                else:
                    f.write("✓ No obvious signs of steganography\n")
    
    # Print summary
    print("\nSummary:")
    print("=" * 80)
    print(f"Total images analyzed: {len(image_files)}")
    print(f"Suspicious files found: {len(suspicious_files)}")
    if suspicious_files:
        print("\nSuspicious files:")
        for file in suspicious_files:
            print(f"  - {file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze images for potential steganography')
    parser.add_argument('directory', help='Directory containing images to analyze')
    parser.add_argument('--output', '-o', help='Output file for analysis report')
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    analyze_directory(args.directory, args.output)

if __name__ == '__main__':
    main() 