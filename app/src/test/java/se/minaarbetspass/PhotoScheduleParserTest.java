package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class PhotoScheduleParserTest {
    private PhotoScheduleParser.Token t(String text,int left,int top,int right,int bottom){return new PhotoScheduleParser.Token(text,left,top,right,bottom);}

    @Test public void detectsSwedishMonthAndYear(){
        PhotoScheduleParser.MonthYear my=PhotoScheduleParser.detectMonthYear("OKTOBER 2026",2026,9);
        assertTrue(my.detected);
        assertEquals(2026,my.year);
        assertEquals(10,my.month);
    }

    @Test public void parsesOneClearRangeAndHourOnlyStart(){
        List<PhotoScheduleParser.Token> tokens=Arrays.asList(
            t("1",20,100,40,130),t("TORSDAG",70,100,150,130),t("14",300,100,330,130),t("30",340,100,370,130),t("-",380,100,395,130),t("21",410,100,440,130),t("40",450,100,480,130),
            t("7",20,300,40,330),t("ONSDAG",70,300,150,330),t("Reserv",220,300,285,330),t("7",300,300,320,330),t("-",335,300,350,330),t("16",365,300,395,330),t("00",405,300,435,330)
        );
        List<PhotoScheduleParser.Candidate> out=PhotoScheduleParser.parse(tokens,2026,10);
        assertEquals(2,out.size());
        assertEquals(1,out.get(0).day);assertEquals("14:30",out.get(0).start);assertEquals("21:40",out.get(0).end);
        assertEquals(7,out.get(1).day);assertEquals("07:00",out.get(1).start);assertEquals("16:00",out.get(1).end);
    }

    @Test public void skipsRowsWithMoreThanOnePossibleRange(){
        List<PhotoScheduleParser.Token> tokens=Arrays.asList(
            t("14",20,100,45,130),t("6",300,100,320,130),t("-",330,100,340,130),t("12",350,100,380,130),t("30",390,100,420,130),t("-",435,100,445,130),t("15",460,100,490,130),t("30",500,100,530,130),t("-",545,100,555,130),t("21",570,100,600,130),t("40",610,100,640,130)
        );
        assertTrue(PhotoScheduleParser.parse(tokens,2026,10).isEmpty());
    }

    @Test public void reviewKeepsAmbiguousDayWithoutGuessingTimes(){
        List<PhotoScheduleParser.Token> tokens=Arrays.asList(
            t("14",20,100,45,130),t("6",300,100,320,130),t("-",330,100,340,130),t("12",350,100,380,130),t("30",390,100,420,130),t("-",435,100,445,130),t("15",460,100,490,130),t("30",500,100,530,130),t("-",545,100,555,130),t("21",570,100,600,130),t("40",610,100,640,130)
        );
        List<PhotoScheduleParser.Candidate> out=PhotoScheduleParser.parseForReview(tokens,2026,10);
        assertEquals(1,out.size());
        assertEquals(14,out.get(0).day);
        assertTrue(out.get(0).uncertain);
        assertEquals("",out.get(0).start);
        assertEquals("",out.get(0).end);
    }

    @Test public void reviewMarksClearRangeAsCertain(){
        List<PhotoScheduleParser.Token> tokens=Arrays.asList(
            t("2",20,100,40,130),t("15",300,100,330,130),t("30",340,100,370,130),t("-",380,100,395,130),t("20",410,100,440,130),t("30",450,100,480,130)
        );
        List<PhotoScheduleParser.Candidate> out=PhotoScheduleParser.parseForReview(tokens,2026,10);
        assertEquals(1,out.size());
        assertFalse(out.get(0).uncertain);
        assertEquals("15:30",out.get(0).start);
        assertEquals("20:30",out.get(0).end);
    }
}
