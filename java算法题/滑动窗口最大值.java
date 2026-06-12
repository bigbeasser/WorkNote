import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class 滑动窗口最大值 {
    public static void main(String[] args) {
        LocalDate curveDate = LocalDate.parse("2026-03-11", DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        LocalDate movementDate = LocalDate.parse("2026-03-11", DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        if (movementDate.isBefore(curveDate)){
            System.out.println(111);
        }
    }
}
