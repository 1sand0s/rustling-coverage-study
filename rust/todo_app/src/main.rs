mod tasks;
mod ui;

use tasks::TaskManager;
use ui::{display_menu, handle_user_input};

fn main() {
    let mut task_manager = TaskManager::new();

    loop {
        display_menu();
        let choice = handle_user_input();

        match choice {
            1 => {
                println!("Enter the task description:");
                let mut description = String::new();
                std::io::stdin().read_line(&mut description).expect("Failed to read line");
                task_manager.add_task(description.trim().to_string());
                println!("Task added!");
            },
            2 => {
                task_manager.list_tasks().iter().enumerate().for_each(|(i, task)| println!("{}. {}", i + 1, task));
                println!("Enter the number of the task to mark as completed:");
                let mut input = String::new();
                std::io::stdin().read_line(&mut input).expect("Failed to read line");
                let index: usize = input.trim().parse().expect("Invalid number");
                task_manager.complete_task(index - 1);
                println!("Task marked as completed!");
            },
            3 => {
                task_manager.list_tasks().iter().for_each(|task| println!("{}", task));
            },
            4 => {
                task_manager.save_tasks("tasks.txt").expect("Failed to save tasks");
                println!("Tasks saved.");
            },
            5 => {
                task_manager.load_tasks("tasks.txt").expect("Failed to load tasks");
                println!("Tasks loaded.");
            },
            6 => {
                println!("Exiting...");
                break;
            },
            _ => println!("Invalid choice! Please try again."),
        }
    }
}

#[cfg(test)]
mod tests;
