package se.minaarbetspass;

final class CombinedDayState {
    static final int BOTH_FREE=0;
    static final int MINE_ONLY=1;
    static final int LENIE_ONLY=2;
    static final int BOTH_WORK=3;
    private CombinedDayState(){}

    static int of(int mine,int lenie){
        boolean m=mine>0,l=lenie>0;
        if(m&&l)return BOTH_WORK;
        if(m)return MINE_ONLY;
        if(l)return LENIE_ONLY;
        return BOTH_FREE;
    }

    static String label(int state){
        if(state==MINE_ONLY)return "Bara jag";
        if(state==LENIE_ONLY)return "Bara Lenie";
        if(state==BOTH_WORK)return "Båda jobbar";
        return "Båda lediga";
    }
}
