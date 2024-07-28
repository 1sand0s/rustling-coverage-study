use std::fs::File;
use std::io::{self, BufRead, Write};
use std::path::Path;

#[derive(Debug, PartialEq)]
pub struct Task {
    pub description: String,
    pub completed: bool,
}

impl Task {
    pub fn new(description: String) -> Task {
        Task {
            description,
            completed: false,
        }
    }
}

pub struct TaskManager {
    pub tasks: Vec<Task>,
}

impl TaskManager {
    pub fn new() -> TaskManager {
        TaskManager { tasks: Vec::new() }
    }

    pub fn add_task(&mut self, description: String) {
        let task = Task::new(description);
        self.tasks.push(task);
    }

    pub fn complete_task(&mut self, index: usize) {
        if index < self.tasks.len() {
            self.tasks[index].completed = true;
        }
    }

    pub fn list_tasks(&self) -> Vec<String> {
        self.tasks.iter().map(|task| {
            format!(
                "[{}] {}",
                if task.completed { "x" } else { " " },
                task.description
            )
        }).collect()
    }

    pub fn save_tasks(&self, filename: &str) -> io::Result<()> {
        let path = Path::new(filename);
        let mut file = File::create(&path)?;
        for task in &self.tasks {
            writeln!(file, "{}|{}", task.description, task.completed)?;
        }
        Ok(())
    }

    pub fn load_tasks(&mut self, filename: &str) -> io::Result<()> {
        let path = Path::new(filename);
        let file = File::open(&path)?;
        let reader = io::BufReader::new(file);
        self.tasks.clear();
        for line in reader.lines() {
            let line = line?;
            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() == 2 {
                let task = Task {
                    description: parts[0].to_string(),
                    completed: parts[1] == "true",
                };
                self.tasks.push(task);
            }
        }
        Ok(())
    }
}
