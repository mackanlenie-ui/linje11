package se.minaarbetspass;

import org.junit.Test;
import static org.junit.Assert.*;

public class PhotoImportDraftTest {
    @Test public void normalizesCommonEditedTimeFormats(){
        assertEquals("07:00",PhotoImportDraft.normalizeTime("7"));
        assertEquals("07:30",PhotoImportDraft.normalizeTime("7.30"));
        assertEquals("15:40",PhotoImportDraft.normalizeTime("1540"));
        assertEquals("21:05",PhotoImportDraft.normalizeTime("21:05"));
        assertNull(PhotoImportDraft.normalizeTime("25:00"));
    }

    @Test public void editingAnUncertainDraftMakesItImportable(){
        PhotoScheduleParser.Candidate c=new PhotoScheduleParser.Candidate(14,"","",true);
        PhotoImportDraft d=new PhotoImportDraft(c);
        assertFalse(d.canImport());
        assertTrue(d.applyEdit(14,"06:00","21:40"));
        assertTrue(d.canImport());
        assertFalse(d.uncertain);
    }

    @Test public void signatureUsesNormalizedDayAndTimes(){
        long day=1770246000000L;
        assertEquals(
            PhotoImportDraft.signature(day,"07:00","16:00"),
            PhotoImportDraft.signature(day+12345L,"7","16")
        );
    }
}
