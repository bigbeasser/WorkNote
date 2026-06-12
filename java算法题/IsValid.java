import java.util.Stack;

public class IsValid {

    /**
     * 给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s ，判断字符串是否有效。
     *
     * 有效字符串需满足：
     *
     * 左括号必须用相同类型的右括号闭合。
     * 左括号必须以正确的顺序闭合。
     * 每个右括号都有一个对应的相同类型的左括号。
     * @param args
     */

    public static void main(String[] args) {


    }




    public static boolean isValid(String s) {
        char[] charArray = s.toCharArray();
        if (charArray.length % 2 != 0) return false;

        Stack<Character> characters = new Stack<>();
        for (char c : charArray) {
            if(c =='(' || c == '[' || c == '{'){
                characters.push( c);
            }else {
                if (characters.isEmpty()) return false;
                char pop = characters.pop();
                if (c == ')' && pop != '(') return false;
                if (c == '}' && pop != '{') return false;
                if (c == ']' && pop != '[') return false;
            }

        }

        return characters.isEmpty();
    }
}
