import utils.ListNode;

import java.util.ArrayList;

/**
 * 将两个升序链表合并为一个新的 升序 链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。
 */


public class MergeTwoLists {

    public static void main(String[] args) {

    }

    public ListNode mergeTwoListsMethod(ListNode list1, ListNode list2) {
        ArrayList<Integer> arrayList = new ArrayList<>();
        while (list1 != null) {
            arrayList.add(list1.val);
            list1 = list1.next;
        }
        while (list2 != null) {
            arrayList.add(list2.val);
            list2 = list2.next;
        }
        if (arrayList.size() == 0) return null;
        arrayList.sort(Integer::compareTo);


        ListNode node = new ListNode();
        ListNode tempNode = node;
        for (int i = 0; i < arrayList.size(); i++) {
            tempNode.next = new ListNode(arrayList.get(i));
            tempNode = tempNode.next;
        }

        return tempNode.next;

    }

    public ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        if (l1 == null) {
            return l2;
        }
        else if (l2 == null) {
            return l1;
        }
        else if (l1.val < l2.val) {
            l1.next = mergeTwoLists(l1.next, l2);
            return l1;
        }
        else {
            l2.next = mergeTwoLists(l1, l2.next);
            return l2;
        }

    }


}
