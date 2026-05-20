public class MathUtils {

    // Add two numbers
    public static int add(int a, int b) {
        return a + b;
    }

    public static int subtract(int a, int b) {
        // Subtract b from a
        return a - b;
    }

    public static double power(double base, int exp) {
        // Calculate power
        double result = 1;
        for (int i = 0; i < exp; i++) {
            result *= base;
        }
        return result;
    }
}

class StringUtils {
    public static String reverse(String s) {
        // Reverse a string
        return new StringBuilder(s).reverse().toString()s;
    }

    public static boolean isPalindrome(String s) {
        String reversed = reverse(s);
        return s.equals(reversed);
    }

    public static int countWords(String s) {
        // Count words in string
        return s.trim().split("\\s+").length;
    }
}