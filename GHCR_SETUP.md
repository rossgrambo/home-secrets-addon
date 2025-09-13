# GitHub Container Registry Setup

This document explains how to set up automated builds and publishing to GitHub Container Registry (GHCR) for the Home Secrets add-on.

## Immediate Fix

The add-on should now install correctly because the `image` line has been commented out in `config.yaml`. Home Assistant will build the image locally during installation.

## Setting Up Automated Builds

To enable automated image builds and publishing:

### 1. Enable GitHub Actions

GitHub Actions is already configured with the workflow in `.github/workflows/build.yml`. This will automatically:
- Build images for all supported architectures (aarch64, amd64, armv7)
- Push to GitHub Container Registry
- Tag images with version numbers

### 2. Configure Repository Permissions

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### 3. Enable Package Visibility

After the first build:
1. Go to your GitHub profile → **Packages**
2. Find the created package (e.g., `aarch64-addon-home-secrets`)
3. Click on it → **Package settings**
4. Under "Danger Zone", change visibility to **Public**
5. Repeat for all architecture packages

### 4. Uncomment Image Line

Once the automated build has run successfully:
1. Edit `addons/home-secrets/config.yaml`
2. Uncomment the image line:
   ```yaml
   image: "ghcr.io/rossgrambo/{arch}-addon-home-secrets"
   ```
3. Commit and push the change

## Build Process

The GitHub Actions workflow will:

1. **Trigger** on pushes to main/master branch
2. **Build** Docker images for each architecture
3. **Push** to `ghcr.io/rossgrambo/{arch}-addon-home-secrets`
4. **Tag** with both SHA and version number
5. **Create** version-specific tags from config.yaml

## Versioning

To release a new version:
1. Update the `version` field in `addons/home-secrets/config.yaml`
2. Update `addons/home-secrets/CHANGELOG.md`
3. Commit and push to main/master
4. The workflow will automatically create version-tagged images

## Troubleshooting

### Build Fails
- Check the Actions tab in your repository
- Ensure workflow permissions are set correctly
- Verify the Dockerfile builds locally

### Images Not Public
- Make packages public in GitHub package settings
- Images must be public for Home Assistant to pull them

### Version Tags Missing
- Ensure the version in config.yaml follows semantic versioning
- Check that the workflow completed successfully