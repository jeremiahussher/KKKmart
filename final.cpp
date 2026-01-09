#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cctype>  
#include <algorithm>  

class Book {
public:
    std::string title, author, isbn;
    bool available;

    Book(std::string t, std::string a, std::string i)
        : title(t), author(a), isbn(i), available(true) {}
};

class User {
public:
    std::string name, id;
    std::vector<std::string> borrowedBooks;  // List of borrowed ISBNs

    User(std::string n, std::string i) : name(n), id(i) {}
};

// Forward declarations (added for new functions called in main)
void saveBooks(const std::vector<Book>& books);
void adminMenu(std::vector<Book>& books);
void studentMenu(std::vector<Book>& books);

// Function to check if a string is a valid name (letters, spaces, '-' and apostrophe allowed)
bool isValidName(const std::string& str) {
    if (str.empty()) return false; // must not be empty
    for (char c : str) {
        if (!std::isalpha(c) && c != ' ' && c != '-' && c != '\'') {
            return false;
        }
    }
    return true;
}

// Function to check if a string is a valid ISBN (digits only)
bool isValidISBN(const std::string& isbn) {
    if (isbn.empty()) return false;
    for (char c : isbn) {
        if (!std::isdigit(c)) return false;
    }
    return true;
}

// Clean Add Book Function
void addBook(std::vector<Book>& books) {
    std::string title, author, isbn;

    // Input and validate book title
    do {
        std::cout << "Enter Book Title: ";
        std::getline(std::cin, title);

        if (title.empty()) {
            std::cout << "Title cannot be empty.\n";
        } else if (!isValidName(title)) {
            std::cout << "Invalid title. Only letters, spaces, '-' and apostrophes are allowed.\n";
        }
    } while (title.empty() || !isValidName(title));

    // Input and validate book author
    do {
        std::cout << "Enter Book Author: ";
        std::getline(std::cin, author);

        if (author.empty()) {
            std::cout << "Author name cannot be empty.\n";
        } else if (!isValidName(author)) {
            std::cout << "Invalid author name. Only letters, spaces, '-' and apostrophes are allowed.\n";
        }
    } while (author.empty() || !isValidName(author));

    // Input and validate ISBN
    do {
        std::cout << "Enter Book Number (ISBN): ";
        std::getline(std::cin, isbn);

        if (!isValidISBN(isbn)) {
            std::cout << "Invalid ISBN. Only digits are allowed.\n";
        } else {
            // Check for duplicate ISBN
            bool duplicate = false;
            for (const auto& book : books) {
                if (book.isbn == isbn) {
                    duplicate = true;
                    break;
                }
            }
            if (duplicate) {
                std::cout << "A book with this ISBN already exists. Please enter a unique ISBN.\n";
                isbn.clear();  // Force re-input
            }
        }
    } while (!isValidISBN(isbn) || isbn.empty());

    // Add book to the list
    books.push_back(Book(title, author, isbn));
    std::cout << "Book added successfully!\n";

    // CHANGE: Save to file immediately after adding to prevent data loss
    saveBooks(books);
}

// List all books (updated to show availability status)
void listBooks(const std::vector<Book>& books) {
    if (books.empty()) {
        std::cout << "No books available.\n";
        return;
    }

    std::cout << "\nAll Books:\n";  // Changed from "Available Books" to "All Books" for accuracy
    for (const auto& book : books) {
        std::cout << "Title: " << book.title
                  << ", Author: " << book.author
                  << ", ISBN: " << book.isbn
                  << ", Status: " << (book.available ? "Available" : "Borrowed") << "\n";  
    }
}

// Search books by title or author
void searchBooks(const std::vector<Book>& books) {
    std::string query;
    std::cout << "Enter book title or author to search: ";
    std::getline(std::cin, query);

    bool found = false;

    for (const auto& book : books) {
        if (book.title.find(query) != std::string::npos ||
            book.author.find(query) != std::string::npos) {
            std::cout << "Found - Title: " << book.title
                      << ", Author: " << book.author
                      << ", ISBN: " << book.isbn << "\n";
            found = true;
        }
    }

    if (!found) {
        std::cout << "No books found matching the query.\n";
    }
}

// Save books to file (added error handling)
void saveBooks(const std::vector<Book>& books) {
    std::ofstream file("books.txt");
    if (!file) {
        std::cerr << "Error: Could not open books.txt for saving.\n";
        return;
    }

    for (const auto& book : books) {
        file << book.title << ","
             << book.author << ","
             << book.isbn << ","
             << book.available << "\n";
    }
    file.close();
}

// Load books from file (added check for malformed lines)
void loadBooks(std::vector<Book>& books) {
    std::ifstream file("books.txt");
    if (!file) return;

    std::string line;
    while (std::getline(file, line)) {
        std::string title, author, isbn, availableStr;
        size_t pos;

        pos = line.find(',');
        if (pos == std::string::npos) continue;  // Skip malformed lines
        title = line.substr(0, pos);
        line.erase(0, pos + 1);

        pos = line.find(',');
        if (pos == std::string::npos) continue;
        author = line.substr(0, pos);
        line.erase(0, pos + 1);

        pos = line.find(',');
        if (pos == std::string::npos) continue;
        isbn = line.substr(0, pos);
        line.erase(0, pos + 1);

        availableStr = line;

        Book book(title, author, isbn);
        book.available = (availableStr == "1");
        books.push_back(book);
    }
    file.close();
}

void editBook(std::vector<Book>& books) {
    std::string isbn;
    std::cout << "Enter ISBN of the book to edit: ";
    std::getline(std::cin, isbn);

    for (auto& book : books) {
        if (book.isbn == isbn) {
            std::cout << "Editing Book: " << book.title << "\n";
            std::cout << "New Title (leave empty to keep current): ";
            std::string newTitle;
            std::getline(std::cin, newTitle);
            if (!newTitle.empty()) book.title = newTitle;

            std::cout << "New Author (leave empty to keep current): ";
            std::string newAuthor;
            std::getline(std::cin, newAuthor);
            if (!newAuthor.empty()) book.author = newAuthor;

            std::cout << "Book info updated successfully.\n";
            return;
        }
    }

    std::cout << "Book with that ISBN not found.\n";
}

// Delete book by ISBN with confirmation
void deleteBook(std::vector<Book>& books) {
    std::string isbn;
    std::cout << "Enter Book number of the book to delete: ";
    std::getline(std::cin, isbn);

    for (auto it = books.begin(); it != books.end(); ++it) {
        if (it->isbn == isbn) {
            char confirm;
            std::cout << "Are you sure you want to delete this book? (y/n): ";
            std::cin >> confirm;
            std::cin.ignore(); // Clear the newline from buffer

            if (confirm == 'y' || confirm == 'Y') {
                books.erase(it);
                std::cout << "Book deleted successfully.\n";
            } else {
                std::cout << "Delete canceled.\n";
            }
            return; // Stop after handling one book
        }
    }

    std::cout << "Book with that ISBN not found.\n";
}

// This handles all admin operations (add, list, search, edit, delete, exit)
void adminMenu(std::vector<Book>& books) {
    int choice;
    do {
        std::cout << "\nAdmin Library Management System\n";
        std::cout << "1. Add Book\n";
        std::cout << "2. List Books\n";
        std::cout << "3. Search Books\n";
        std::cout << "4. Edit Books\n";
        std::cout << "5. Delete Books\n";
        std::cout << "6. Exit\n";
        std::cout << "Enter your choice: ";

        std::cin >> choice;
        std::cin.ignore(); // Clear newline from input buffer

        switch (choice) {
            case 1:
                addBook(books);
                break;
            case 2:
                listBooks(books);
                break;
            case 3:
                searchBooks(books);
                break;
            case 4:
                editBook(books);
                break;
            case 5:
                deleteBook(books);
                break;
            case 6:
                saveBooks(books);  // Ensure final save on exit
                std::cout << "Data saved. Exiting admin menu.\n";
                break;
            default:
                std::cout << "Invalid choice. Please try again.\n";
        }
    } while (choice != 6);
}

// This is Student Menu. For students that can only borrow and return books.
void studentMenu(std::vector<Book>& books) {
    std::string studentName, studentID;
    std::cout << "Enter your name: ";
    std::getline(std::cin, studentName);
    std::cout << "Enter your student ID: ";
    std::getline(std::cin, studentID);

    User currentUser(studentName, studentID);  // Create a temporary user for this session
    int choice;
    do {
        std::cout << "\nStudent Library Menu\n";
        std::cout << "1. List Books\n";
        std::cout << "2. Search Books\n";
        std::cout << "3. Borrow Book\n";
        std::cout << "4. Return Book\n";
        std::cout << "5. View My Borrowed Books\n";
        std::cout << "6. Exit\n";
        std::cout << "Enter your choice: ";

        std::cin >> choice;
        std::cin.ignore();

        switch (choice) {
            case 1:
                listBooks(books);
                break;
            case 2:
                searchBooks(books);
                break;
            case 3: {  // Borrow book
                std::string isbn;
                std::cout << "Enter ISBN of the book to borrow: ";
                std::getline(std::cin, isbn);
                bool borrowed = false;  
                for (auto& book : books) {
                    if (book.isbn == isbn && book.available) {
                        book.available = false;
                        currentUser.borrowedBooks.push_back(isbn);
                        std::cout << "Book borrowed successfully!\n";
                        saveBooks(books);  // Save changes
                        borrowed = true;
                        break;
                    }
                }
                if (!borrowed) std::cout << "Book not available or not found.\n";  // **FIX: Now checks the flag instead of out-of-scope 'book'**
                break;
            }
            case 4: {  // Return book
                std::string isbn;
                std::cout << "Enter ISBN of the book to return: ";
                std::getline(std::cin, isbn);
                for (auto& book : books) {
                    if (book.isbn == isbn && !book.available) {
                        book.available = true;
                        // Remove from user's borrowed list
                        auto it = std::find(currentUser.borrowedBooks.begin(), currentUser.borrowedBooks.end(), isbn);  // **FIX: std::find now works with <algorithm> included**
                        if (it != currentUser.borrowedBooks.end()) currentUser.borrowedBooks.erase(it);
                        std::cout << "Book returned successfully!\n";
                        saveBooks(books);  // Save changes
                        break;
                    }
                }
                std::cout << "Book not found in your borrowed list.\n";
                break;
            }
            case 5: {  // View borrowed books
                if (currentUser.borrowedBooks.empty()) {
                    std::cout << "You have no borrowed books.\n";
                } else {
                    std::cout << "Your borrowed books:\n";
                    for (const auto& isbn : currentUser.borrowedBooks) {
                        for (const auto& book : books) {
                            if (book.isbn == isbn) {
                                std::cout << "Title: " << book.title << ", Author: " << book.author << "\n";
                            }
                        }
                    }
                }
                break;
            }
            case 6:
                std::cout << "Exiting student menu.\n";
                break;
            default:
                std::cout << "Invalid choice. Please try again.\n";
        }
    } while (choice != 6);
}


// This replaces the original main. It loads books, shows a welcome, and handles role selection.
int main() {
    std::vector<Book> books;

    // Load books from file at program start
    loadBooks(books);

    std::cout << "=====================================\n";
    std::cout << "      Welcome to the Library System   \n";
    std::cout << "=====================================\n";

    int roleChoice;

    // Role selection
    do {
        std::cout << "\nSelect your role:\n";
        std::cout << "1. Admin\n";
        std::cout << "2. Student\n";
        std::cout << "3. Exit\n";  
        std::cout << "Enter your choice: ";
        std::cin >> roleChoice;
        std::cin.ignore(); 

        if (roleChoice == 1) {
            adminMenu(books);   
        } else if (roleChoice == 2) {
            studentMenu(books); 
        } else if (roleChoice == 3) {
            std::cout << "Exiting the system.\n";
        } else {
            std::cout << "Invalid choice. Please select 1 for Admin, 2 for Student, or 3 to Exit.\n";
        }
    } while (roleChoice != 3); 

    return 0;

}
