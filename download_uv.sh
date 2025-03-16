#!/bin/bash
set -e

# Create destination binaries directory
mkdir -p ./src-tauri/binaries

# Install uv temporarily
mise install-into uv@latest ./temp_uv

# Get platform information - remove the leading "uv-" if it exists
platform_dir=$(ls ./temp_uv)
platform_name=${platform_dir#uv-}  # This removes "uv-" prefix if it exists
echo "Detected platform: $platform_name"

# Copy and rename binaries - we only need uv
if [ -f "./temp_uv/$platform_dir/uv" ]; then
  cp "./temp_uv/$platform_dir/uv" "./src-tauri/binaries/uv-$platform_name"
  echo "Copied uv to ./src-tauri/binaries/uv-$platform_name"
fi

# Clean up
rm -rf ./temp_uv
echo "Temporary files cleaned up"
