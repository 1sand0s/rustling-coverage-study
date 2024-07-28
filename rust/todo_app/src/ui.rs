use std::io::{self, Write};

pub fn display_menu() {
    println!("\nTo-Do List:");
    println!("1. Add task");
    println!("2. Complete task");
    println!("3. List tasks");
    println!("4. Save tasks");
    println!("5. Load tasks");
    println!("6. Exit");
    print!("Enter your choice: ");
    io::stdout().flush().unwrap();
}

pub fn handle_user_input() -> u32 {
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Failed to read line");
    input.trim().parse().unwrap_or(0)
}
