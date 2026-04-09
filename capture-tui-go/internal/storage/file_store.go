package storage

import (
	"fmt"
	"os"
	"path/filepath"
)

// FileStore handles file system operations
type FileStore struct {
	rootDir string
}

// NewFileStore creates a new file store
func NewFileStore(rootDir string) *FileStore {
	return &FileStore{rootDir: rootDir}
}

// EnsureDir ensures a directory exists
func (fs *FileStore) EnsureDir(path string) (string, error) {
	fullPath := filepath.Join(fs.rootDir, path)
	if err := os.MkdirAll(fullPath, 0755); err != nil {
		return "", fmt.Errorf("failed to create directory: %w", err)
	}
	return fullPath, nil
}

// Write writes content to a file
func (fs *FileStore) Write(path string, content string) (string, error) {
	fullPath := filepath.Join(fs.rootDir, path)
	dir := filepath.Dir(fullPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return "", fmt.Errorf("failed to create directory: %w", err)
	}

	if err := os.WriteFile(fullPath, []byte(content), 0644); err != nil {
		return "", fmt.Errorf("failed to write file: %w", err)
	}

	return fullPath, nil
}

// Read reads content from a file
func (fs *FileStore) Read(path string) (string, error) {
	fullPath := filepath.Join(fs.rootDir, path)
	data, err := os.ReadFile(fullPath)
	if err != nil {
		return "", fmt.Errorf("failed to read file: %w", err)
	}
	return string(data), nil
}

// Exists checks if a path exists
func (fs *FileStore) Exists(path string) bool {
	fullPath := filepath.Join(fs.rootDir, path)
	_, err := os.Stat(fullPath)
	return err == nil
}

// IsDir checks if a path is a directory
func (fs *FileStore) IsDir(path string) bool {
	fullPath := filepath.Join(fs.rootDir, path)
	info, err := os.Stat(fullPath)
	if err != nil {
		return false
	}
	return info.IsDir()
}

// ListDirs lists all directories in a path
func (fs *FileStore) ListDirs(path string) ([]string, error) {
	fullPath := filepath.Join(fs.rootDir, path)
	entries, err := os.ReadDir(fullPath)
	if err != nil {
		if os.IsNotExist(err) {
			return []string{}, nil
		}
		return nil, fmt.Errorf("failed to list directories: %w", err)
	}

	var dirs []string
	for _, entry := range entries {
		if entry.IsDir() && !strings.HasPrefix(entry.Name(), ".") {
			dirs = append(dirs, entry.Name())
		}
	}
	return dirs, nil
}

// ListFiles lists all files matching a pattern
func (fs *FileStore) ListFiles(path string, pattern string) ([]string, error) {
	fullPath := filepath.Join(fs.rootDir, path)
	matches, err := filepath.Glob(filepath.Join(fullPath, pattern))
	if err != nil {
		return nil, fmt.Errorf("failed to list files: %w", err)
	}

	// Convert to relative paths
	var relative []string
	for _, match := range matches {
		rel, err := filepath.Rel(fs.rootDir, match)
		if err == nil {
			relative = append(relative, rel)
		}
	}
	return relative, nil
}

// Walk walks the directory tree
func (fs *FileStore) Walk(path string, fn func(path string, info os.FileInfo) error) error {
	fullPath := filepath.Join(fs.rootDir, path)
	return filepath.Walk(fullPath, func(p string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(fs.rootDir, p)
		if err != nil {
			return err
		}
		return fn(rel, info)
	})
}

// Delete removes a file or directory
func (fs *FileStore) Delete(path string) error {
	fullPath := filepath.Join(fs.rootDir, path)
	return os.RemoveAll(fullPath)
}

// Move moves a file or directory
func (fs *FileStore) Move(src, dst string) error {
	srcPath := filepath.Join(fs.rootDir, src)
	dstPath := filepath.Join(fs.rootDir, dst)

	// Ensure destination directory exists
	dir := filepath.Dir(dstPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create destination directory: %w", err)
	}

	return os.Rename(srcPath, dstPath)
}
