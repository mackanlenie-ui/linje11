package se.minaarbetspass;

import org.junit.Test;
import static org.junit.Assert.*;

public class PhotoImageMathTest {
    @Test public void contrastEnhancementKeepsWhiteAndBlackStable(){
        assertEquals(0xffffffff,PhotoImageMath.enhanceArgb(0xffffffff));
        assertEquals(0xff000000,PhotoImageMath.enhanceArgb(0xff000000));
    }

    @Test public void contrastEnhancementPushesLightGrayLighter(){
        int out=PhotoImageMath.enhanceArgb(0xffc0c0c0);
        int gray=(out>>16)&0xff;
        assertTrue(gray>0xc0);
    }

    @Test public void contrastEnhancementOutputsNeutralGray(){
        int out=PhotoImageMath.enhanceArgb(0xffc08040);
        assertEquals((out>>16)&0xff,(out>>8)&0xff);
        assertEquals((out>>8)&0xff,out&0xff);
    }
}
