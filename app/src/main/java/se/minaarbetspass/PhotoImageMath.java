package se.minaarbetspass;

final class PhotoImageMath {
    private PhotoImageMath(){}

    static int enhanceArgb(int argb){
        int r=(argb>>16)&255,g=(argb>>8)&255,b=argb&255;
        int gray=(r*30+g*59+b*11)/100;
        int enhanced=clamp((int)Math.round((gray-128)*1.45+128));
        return 0xff000000|(enhanced<<16)|(enhanced<<8)|enhanced;
    }

    private static int clamp(int v){return v<0?0:v>255?255:v;}
}
