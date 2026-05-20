// Utility functions for testing

function calculateTotal(price, quantity) {
    // Multiply price by quantity
    // Returns total cost
    return price * quantity;
}

function getUserById(id) {
    // Find user in database
    return users.find(u => u.id === id);
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

class ShoppingCart {
    constructor(userId) {
        // Initialize empty cart
        this.userId = userId;
        this.items = [];
    }

    addItem(item) {
        // Add item to cart
        this.items.push(item);
    }

    removeItem(itemId) {
        this.items = this.items.filter(i => i.id !== itemId);
    }

    getTotal() {
        // Sum all item prices
        return this.items.reduce((sum, item) => sum + item.price, 0);
    }
}