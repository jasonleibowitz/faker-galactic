# 📜 Captain's Log: Release {{ VERSION }}

## 🎯 Mission Briefing

Prepare the ship for deployment to the PyPI Quadrant.

## ✅ Pre-Flight Checklist

- [ ] **Warp core stable** - All tests passing
- [ ] **Shields up** - Type checks passing
- [ ] **Sensors calibrated** - Linting passing
- [ ] **Captain's log updated** - CHANGELOG.md has entry for {{ VERSION }}
- [ ] **Stardate confirmed** - Version in pyproject.toml matches {{ VERSION }}

## 🗺️ Navigation Coordinates

### 📋 Changes in this release:
{{ CHANGES }}

View complete history in the [Captain's Log](../CHANGELOG.md#{{ VERSION_ANCHOR }})

## 🚀 Post-Merge Protocol

Once this PR warps into master, the ship's computer will:

1. 🏷️ Create git tag `v{{ VERSION }}`
2. 📦 Build the package
3. 🚢 Transmit to PyPI at maximum warp
4. 📝 Generate GitHub Release notes

**Make it so.** 🖖
