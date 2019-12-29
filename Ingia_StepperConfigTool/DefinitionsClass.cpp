#include "DefinitionsClass.h"

uint16_t DefinitionsClass::getCantParam( const DefinitionsClass::parameter_t paramArray[] ) {
    uint16_t i=0;
    while( paramArray[i].name != "END_PARAMETER" )
        i++;
    return i;
}

const DefinitionsClass::parameter_t DefinitionsClass::powerStep01_parameters[] = {
    {
        .name = "STEP_MODE",
        .inputType = DISCRETE,
        .opc ="STEP_MODE_FULL|STEP_MODE_HALF|STEP_MODE_1_4|STEP_MODE_1_8|STEP_MODE_1_16|STEP_MODE_1_32|STEP_MODE_1_64|STEP_MODE_1_128|STEP_MODE_1_256",
        .desc ="Step Mode"
    },
    {
        .name ="I_GATE",
        .inputType = DISCRETE,
        .opc = "4 mA|8 mA|16 mA|24 mA|32 mA|64 mA|96 mA",
        .desc ="Sink or source current used by gate driving circuitry"
    },
    {
        .name = "T_BOOST",
        .inputType = DISCRETE,
        .opc="0 ns|125 ns|250 ns|375 ns|500 ns|750 ns|1000 ns",
        .desc="Step Mode"
    },
    {
        .name = "TCC",
        .inputType = MULTIPLES,
        .opc = "125-3750-ns",
        .desc = "Duration of constant current phase during gate turn-on and turn-off \n(125-3750ns)"
    },
    {
        .name = "T_BLANK",
        .inputType = DISCRETE,
        .opc = "125 ns|250 ns|375 ns|500 ns|625 ns|750 ns|875 ns|1000 ns",
        .desc = "Duration of the blanking of the current sensing comparators"
    },
    {
        .name = "T_DEADTIME",
        .inputType = MULTIPLES,
        .opc = "125-4000-ns",
        .desc = "Deadtime duration between gate turn-off and opposite gate turn-on \n(125-4000ns)"
    },
    {
        .name = "TVAL_HOLD",
        .inputType = MULTIPLES,
        .opc = "7.8-1000-mV",
        .desc = "(7.8-1000mV)"
    },
    {
        .name = "TVAL_RUN",
        .inputType = MULTIPLES,
        .opc = "7.8-1000-mV",
        .desc = "(7.8-1000mV)"
    },
    {
        .name = "TVAL_ACC",
        .inputType = MULTIPLES,
        .opc = "7.8-1000-mV",
        .desc = "(7.8-1000mV)"
    },
    {
        .name = "TVAL_DEC",
        .inputType = MULTIPLES,
        .opc = "7.8-1000-mV",
        .desc = "(7.8-1000mV)"
    },
    {
        .name = "TOFF_FAST",
        .inputType = DISCRETE,
        .opc = "2 us|4 us|6 us|8 us|10 us|12 us|14 us|16 us|18 us|20 us|22 us|24 us|26 us|28 us|30 us|32 us",
        .desc = "Maximum fast decay time"
    },
    {
        .name = "FAST_STEP",
        .inputType = DISCRETE,
        .opc = "2 us|4 us|6 us|8 us|10 us|12 us|14 us|16 us|18 us|20 us|22 us|24 us|26 us|28 us|30 us|32 us",
        .desc = "Maximum fall step time"
    },
    {
        .name = "TON_MIN",
        .inputType = MULTIPLES,
        .opc = "0.5-64-us",
        .desc = "(0.5-64us)"
    },
    {
        .name = "TOFF_MIN",
        .inputType = MULTIPLES,
        .opc = "0.5-64-us",
        .desc = "(0.5-64us)"
    },
    {
        .name = "TSW",
        .inputType = MULTIPLES,
        .opc = "4-124-us",
        .desc = "Target switching period (4-124us)"
    },
    { .name = "END_PARAMETER" }
};
