public class maxArea {


    /**
     * 给定一个长度为 n 的整数数组 height 。有 n 条垂线，第 i 条线的两个端点是 (i, 0) 和 (i, height[i]) 。
     * <p>
     * 找出其中的两条线，使得它们与 x 轴共同构成的容器可以容纳最多的水。
     * <p>
     * 返回容器可以储存的最大水量。
     * <p>
     * 说明：你不能倾斜容器。
     */

    public static void main(String[] args) {
        int[] height = {1, 8, 6, 2, 5, 4, 8, 3, 7};
        System.out.println(maxAreaSolution(height));
        System.out.println(maxAreaSolution2(height));
    }

    /**
     * 时间复杂度分析：
     * - 使用双层嵌套循环
     * - 外层循环：left 从 0 到 bottleMax-2，共执行 (bottleMax-1) 次
     * - 内层循环：right 从 left+1 到 bottleMax-1，对于每个 left，执行次数逐渐减少
     * 总执行次数为：(n-1) + (n-2) + ... + 1 = n(n-1)/2（n为数组长度）
     * - 因此时间复杂度为 O(n²)
     * 
     * 空间复杂度分析：
     * - 只使用了几个固定的额外变量：maxArea, bottleMax, left, right, bolltleLength, min, area
     * - 这些变量的数量与输入数组的大小无关
     * - 因此空间复杂度为 O(1)
     */
    public static int maxAreaSolution(int[] height) {
        int maxArea = 0;
        int bottleMax = height.length;
        int left = 0;
        int right = 0;
        for (; left < bottleMax - 1; left++) {
            for (right = left + 1; right < bottleMax; right++) {
                int bolltleLength = right - left;
                int min = Math.min(height[left], height[right]);
                int area = min * bolltleLength;
                if (area > maxArea) {
                    maxArea = area;
                }
            }

        }
        return maxArea;
    }

    public static int maxAreaOptimized(int[] height) {
        int maxArea = 0;
        int left = 0;
        int right = height.length - 1;

        while (left < right) {
            int width = right - left;
            int minHeight = Math.min(height[left], height[right]);
            int currentArea = width * minHeight;
            maxArea = Math.max(maxArea, currentArea);

            // 移动较短的那个指针
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }

        return maxArea;
    }


    /**
     * 优化思路：
     * - 移动较短的指针，可以避免重复计算
     * - 移动的指针，应该与当前指针的数值进行比较
     * - 移动的指针，应该与当前指针的数值进行比较
     */
    public static int maxAreaSolution2(int[] height) {
        int maxArea = 0;
        int left = 0;
        int right = height.length-1;

        while(left < right){
            int width = right - left;
            int min = Math.min(height[left], height[right]);
            int area = width * min;
            if (area > maxArea){
                maxArea = area;
            }
            if (height[left] <= height[right]){
                left ++;
            }else {
                right --;
            }
        }



     return maxArea;
    }
}
