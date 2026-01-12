#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cctype>  
#include <algorithm>  
#include <iomanip> 
#include <regex>
#include <ctime> 
#include <sstream>

// --- DATA CLASSES ---

class Book {
public:
    std::string title, author, isbn;
    bool available;

    Book(std::string t, std::string a, std::string i, bool avail = true)
        : title(t), author(a), isbn(i), available(avail) {}
};

class User {
public:
    std::string name, id;
    std::vector<std::string> borrowedBooks; 

    User(std::string n, std::string i) : name(n), id(i) {}
};

// --- UTILITIES ---

std::string getCurrentTime() {
    std::time_t now = std::time(0);
    char buf[80];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", std::localtime(&now));
    return std::string(buf);
}

void logHistory(const std::string& studentID, const std::string& action, const std::string& isbn) {
    std::ofstream file("history.txt", std::ios::app);
    if (file) {
        file << "[" << getCurrentTime() << "] ID: " << studentID 
             << " | Action: " << action << " | Book Number: " << isbn << "\n";
    }
    file.close();
}

void saveBooks(const std::vector<Book>& books) {
    std::ofstream file("books.txt");
    if (!file) return;
    for (const auto& book : books) {
        file << book.title << "|" << book.author << "|" << book.isbn << "|" << book.available << "\n";
    }
    file.close();
}

void saveUsers(const std::vector<User>& users) {
    std::ofstream file("users.txt");
    if (!file) return;
    for (const auto& u : users) {
        file << u.name << "|" << u.id;
        for (const auto& isbn : u.borrowedBooks) {
            file << "|" << isbn;
        }
        file << "\n";
    }
    file.close();
}

bool isValidStudentID(const std::string& id) {
    const std::regex pattern("^[0-9]{4}-[0-9]{5}-[A-Z]{2}-[0-9]{1}$");
    return std::regex_match(id, pattern);
}

int getSafeInt() {
    int choice;
    while (!(std::cin >> choice)) {
        std::cout << "Invalid input. Please enter a number: ";
        std::cin.clear();
        std::cin.ignore(1000, '\n');
    }
    std::cin.ignore(); 
    return choice;
}

// --- CORE FEATURES ---

void listBooks(const std::vector<Book>& books) {
    if (books.empty()) { std::cout << "\nNo books available.\n"; return; }
    std::cout << "\n" << std::left << std::setw(25) << "TITLE" << std::setw(20) << "AUTHOR" 
              << std::setw(15) << "Book NO" << "STATUS" << "\n";
    std::cout << std::string(75, '-') << "\n";
    for (const auto& b : books) {
        std::cout << std::left << std::setw(25) << b.title.substr(0, 23) 
                  << std::setw(20) << b.author.substr(0, 18) 
                  << std::setw(15) << b.isbn 
                  << (b.available ? "Available" : "Borrowed") << "\n";
    }
}

// --- ADMIN MENU 

void adminMenu(std::vector<Book>& books, std::vector<User>& userList) {
    std::string password;
    std::cout << "\n[ADMIN SECURITY] Enter Admin Password: ";
    std::getline(std::cin, password);

    if (password != "admin123") {
        std::cout << "ACCESS DENIED: Incorrect Password!\n";
        return; 
    }

    int choice;
    do {
        std::cout << "\n[ADMIN MENU]\nHello Admin!\n1. Add Book\n2. List Books\n3. Edit Book\n4. Delete Book\n5. View All History\n6. View Student Accounts\n7. Back\nChoice: ";
        choice = getSafeInt();

        if (choice == 1) {
            std::string t, a, i;
            std::cout << "Title: "; std::getline(std::cin, t);
            std::cout << "Author: "; std::getline(std::cin, a);
            std::cout << "Book Number: "; std::getline(std::cin, i);
            books.push_back(Book(t, a, i));
            saveBooks(books);
            std::cout << "Book added successfully.\n";
        } 
        else if (choice == 2) listBooks(books);
        else if (choice == 3) { 
            std::string isbn;
            std::cout << "Enter Book Number to edit: "; std::getline(std::cin, isbn);
            bool found = false;
            for (auto& b : books) {
                if (b.isbn == isbn) {
                    std::cout << "New Title: "; std::getline(std::cin, b.title);
                    std::cout << "New Author: "; std::getline(std::cin, b.author);
                    saveBooks(books);
                    std::cout << "Book updated successfully!\n";
                    found = true; break;
                }
            }
            if (!found) std::cout << "Book not found.\n";
        } 
        else if (choice == 4) { 
            std::string isbn;
            std::cout << "Enter Book Number to delete: "; std::getline(std::cin, isbn);
            auto it = std::remove_if(books.begin(), books.end(), [&](Book& b){ return b.isbn == isbn; });
            if (it != books.end()) {
                books.erase(it, books.end());
                saveBooks(books);
                std::cout << "Book deleted successfully.\n";
            } else std::cout << "Book Number not found.\n";
        } 
        else if (choice == 5) {
            std::ifstream file("history.txt");
            std::string line;
            if (!file) { std::cout << "No history found.\n"; }
            else { 
                std::cout << "\n--- GLOBAL TRANSACTION HISTORY ---\n";
                while (std::getline(file, line)) std::cout << line << "\n"; 
            }
        }
        else if (choice == 6) { 
            if (userList.empty()) {
                std::cout << "\nNo student accounts registered yet.\n";
            } else {
                std::cout << "\n" << std::left << std::setw(20) << "STUDENT NAME" 
                          << std::setw(20) << "STUDENT ID" 
                          << "BOOKS HELD" << "\n";
                std::cout << std::string(55, '-') << "\n";
                for (const auto& u : userList) {
                    std::cout << std::left << std::setw(20) << u.name 
                              << std::setw(20) << u.id 
                              << u.borrowedBooks.size() << "\n";
                }
            }
        }
    } while (choice != 7);
}

// --- STUDENT MENU ---

void studentMenu(std::vector<Book>& books, std::vector<User>& userList) {
    std::string id;
    int attempts = 0;
    bool loggedIn = false;
    const int BORROW_LIMIT = 3;

    while (attempts < 3) {
        std::cout << "\n[STUDENT LOGIN] Enter Student ID: ";
        std::getline(std::cin, id);
        if (isValidStudentID(id)) { loggedIn = true; break; }
        else { attempts++; std::cout << "Invalid Format! (" << (3 - attempts) << " left)\n"; }
    }
    if (!loggedIn) return;

    User* currentUser = nullptr;
    for (auto& u : userList) if (u.id == id) currentUser = &u;
    if (!currentUser) {
        std::string name;
        std::cout << "New User detected! Enter Name: "; std::getline(std::cin, name);
        userList.push_back(User(name, id));
        currentUser = &userList.back();
        saveUsers(userList);
    }

    int choice;
    do {
        std::cout << "\n--- Student: " << currentUser->name << " ---\n";
        std::cout << "1. List Books\n2. Borrow Book\n3. Return Book\n4. My Borrowed Books (Details)\n5. My Return History\n6. Exit\nChoice: ";
        choice = getSafeInt();

        if (choice == 2) {
            if (currentUser->borrowedBooks.size() >= BORROW_LIMIT) {
                std::cout << "\n[!] ERROR: BORROW LIMIT REACHED (3 books max)!\n";
            } else {
                std::string isbn;
                std::cout << "Enter Book Number to borrow: "; std::getline(std::cin, isbn);
                bool found = false;
                for (auto& b : books) {
                    if (b.isbn == isbn && b.available) {
                        b.available = false;
                        currentUser->borrowedBooks.push_back(isbn);
                        saveBooks(books);
                        saveUsers(userList);
                        logHistory(currentUser->id, "BORROW", isbn);
                        std::cout << "Successfully borrowed: " << b.title << "\n";
                        found = true; break;
                    }
                }
                if (!found) std::cout << "Book unavailable or Book Number incorrect.\n";
            }
        } else if (choice == 3) {
            std::string isbn;
            std::cout << "Enter Book Number to return: "; std::getline(std::cin, isbn);
            auto it = std::find(currentUser->borrowedBooks.begin(), currentUser->borrowedBooks.end(), isbn);
            if (it != currentUser->borrowedBooks.end()) {
                for (auto& b : books) if (b.isbn == isbn) b.available = true;
                currentUser->borrowedBooks.erase(it);
                saveBooks(books);
                saveUsers(userList);
                logHistory(currentUser->id, "RETURN", isbn);
                std::cout << "Book returned successfully.\n";
            } else std::cout << "You aren't holding this book.\n";
        } else if (choice == 1) listBooks(books);
        else if (choice == 4) {
            std::cout << "\n--- YOUR CURRENTLY BORROWED BOOKS ---\n";
            if (currentUser->borrowedBooks.empty()) {
                std::cout << "You have no borrowed books.\n";
            } else {
                std::cout << std::left << std::setw(25) << "TITLE" << std::setw(20) << "AUTHOR" << "Book NO" << "\n";
                std::cout << std::string(65, '-') << "\n";
                for (const auto& b_isbn : currentUser->borrowedBooks) {
                    for (const auto& book : books) {
                        if (book.isbn == b_isbn) {
                            std::cout << std::left << std::setw(25) << book.title.substr(0, 23) 
                                      << std::setw(20) << book.author.substr(0, 18) 
                                      << book.isbn << "\n";
                        }
                    }
                }
            }
        }
        else if (choice == 5) {
            std::ifstream file("history.txt");
            std::string line;
            bool historyFound = false;
            std::cout << "\n--- YOUR RETURN HISTORY ---\n";
            if (file) {
                while (std::getline(file, line)) {
                    if (line.find("ID: " + currentUser->id) != std::string::npos && 
                        line.find("Action: RETURN") != std::string::npos) {
                        std::cout << line << "\n";
                        historyFound = true;
                    }
                }
                if (!historyFound) std::cout << "No return history found.\n";
            }
            file.close();
        }
    } while (choice != 6);
}

// --- MAIN / LOADERS ---

void loadBooks(std::vector<Book>& books) {
    std::ifstream file("books.txt");
    if (!file) return;
    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string t, a, i, avail;
        std::getline(ss, t, '|');
        std::getline(ss, a, '|');
        std::getline(ss, i, '|');
        std::getline(ss, avail, '|');
        if (!t.empty()) books.push_back(Book(t, a, i, (avail == "1")));
    }
}

void loadUsers(std::vector<User>& users) {
    std::ifstream file("users.txt");
    if (!file) return;
    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string name, id, isbn;
        std::getline(ss, name, '|');
        std::getline(ss, id, '|');
        if (name.empty()) continue;
        User u(name, id);
        while (std::getline(ss, isbn, '|')) {
            if (!isbn.empty()) u.borrowedBooks.push_back(isbn);
        }
        users.push_back(u);
    }
}

int main() {
    std::vector<Book> books;
    std::vector<User> userList;
    loadBooks(books);
    loadUsers(userList);

    int role;
    do {
        std::cout << "\n==============================\n";
        std::cout << "   LIBRARY MANAGEMENT SYSTEM  \n";
        std::cout << "==============================\n";
        std::cout << "1. Admin Login\n2. Student Login\n3. Exit\nChoice: ";
        role = getSafeInt();
        if (role == 1) adminMenu(books, userList);
        else if (role == 2) studentMenu(books, userList);
    } while (role != 3);

    return 0;
}
