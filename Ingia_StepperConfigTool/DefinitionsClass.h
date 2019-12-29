#ifndef POWERSTEP_DEFINITIONS_H
#define POWERSTEP_DEFINITIONS_H

#include <QString>

class DefinitionsClass
{
public:
    typedef  enum {
        DISCRETE, MULTIPLES, NUMBER
    } inputType_t;

    typedef struct {
        QString name;
        inputType_t inputType;
        QString opc;
        QString desc;
    } parameter_t;

    typedef  enum {
        STEP_MODE, I_GATE, T_BOOST, TCC, T_BLANK, DEADTIME, TVAL_HOLD, TVAL_RUN,
        TVAL_ACC, TVAL_DEC, TOFF_FAST, FAST_STEP, TON_MIN, TOFF_MIN, TSW,
        CANT_PARAMETROS
    } powerStep01_parametersID_t;

    static const parameter_t powerStep01_parameters[];
    static uint16_t getCantParam( const parameter_t paramArray[] );
};

#endif // POWERSTEP_DEFINITIONS_H
