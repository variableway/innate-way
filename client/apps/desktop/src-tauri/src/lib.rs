use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::Manager;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Category {
    name: String,
    display_name: String,
    count: i32,
    description: String,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            get_platform,
            list_categories,
            create_category,
            delete_category,
            rename_category,
            get_default_category_path
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Innate Capture.", name)
}

#[command]
fn get_platform() -> String {
    let os = std::env::consts::OS.to_string();
    let arch = std::env::consts::ARCH.to_string();
    format!("{}-{}", os, arch)
}

#[command]
fn get_default_category_path() -> Result<String, String> {
    let home = dirs::home_dir().ok_or("Cannot determine home directory")?;
    let path = home.join(".innate").join("categories");
    Ok(path.to_string_lossy().to_string())
}

#[command]
fn list_categories(root_dir: String) -> Result<Vec<Category>, String> {
    let root = PathBuf::from(&root_dir);
    if !root.exists() {
        fs::create_dir_all(&root).map_err(|e| format!("Failed to create directory: {}", e))?;
        return Ok(vec![]);
    }

    let mut categories = Vec::new();
    let entries = fs::read_dir(&root).map_err(|e| format!("Failed to read directory: {}", e))?;

    for entry in entries.flatten() {
        if entry.file_type().map(|t| t.is_dir()).unwrap_or(false) {
            let name = entry.file_name().to_string_lossy().to_string();
            // Skip hidden directories
            if name.starts_with('.') {
                continue;
            }
            let count = fs::read_dir(entry.path())
                .map(|entries| entries.count() as i32)
                .unwrap_or(0);
            categories.push(Category {
                display_name: name.clone(),
                name,
                count,
                description: String::new(),
            });
        }
    }

    categories.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(categories)
}

#[command]
fn create_category(root_dir: String, name: String, display_name: Option<String>, description: Option<String>) -> Result<Category, String> {
    let root = PathBuf::from(&root_dir);
    let dir = root.join(&name);

    if dir.exists() {
        return Err(format!("Category '{}' already exists", name));
    }

    // Check max categories
    let existing = list_categories(root_dir)?;
    if existing.len() >= 10 {
        return Err("Maximum 10 categories allowed".to_string());
    }

    fs::create_dir_all(&dir).map_err(|e| format!("Failed to create category: {}", e))?;

    Ok(Category {
        display_name: display_name.unwrap_or_else(|| name.clone()),
        name,
        count: 0,
        description: description.unwrap_or_default(),
    })
}

#[command]
fn delete_category(root_dir: String, name: String) -> Result<(), String> {
    let dir = PathBuf::from(&root_dir).join(&name);
    if !dir.exists() {
        return Err(format!("Category '{}' not found", name));
    }
    fs::remove_dir_all(&dir).map_err(|e| format!("Failed to delete category: {}", e))
}

#[command]
fn rename_category(root_dir: String, old_name: String, new_name: String) -> Result<Category, String> {
    let root = PathBuf::from(&root_dir);
    let old_dir = root.join(&old_name);
    let new_dir = root.join(&new_name);

    if !old_dir.exists() {
        return Err(format!("Category '{}' not found", old_name));
    }
    if new_dir.exists() {
        return Err(format!("Category '{}' already exists", new_name));
    }

    fs::rename(&old_dir, &new_dir).map_err(|e| format!("Failed to rename: {}", e))?;

    Ok(Category {
        display_name: new_name.clone(),
        name: new_name,
        count: 0,
        description: String::new(),
    })
}
