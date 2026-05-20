// TypeScript test file

interface User {
    id: number;
    name: string;
    email: string;
}

function greetUser(user: User): string {
    // Generate greeting message
    return `Hello, ${user.name}!`;
}

function validateEmail(email: string): boolean {
    // Check email format
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function calculateDiscount(price: number, percent: number): number {
    return price - (price * percent / 100);
}

class UserService {
    private users: User[] = [];

    addUser(user: User): void {
        // Add new user to list
        this.users.push(user);
    }

    getUserById(id: number): User | undefined {
        // Find user by id
        return this.users.find(u => u.id === id);
    }

    deleteUser(id: number): void {
        this.users = this.users.filter(u => u.id !== id);
    }
}