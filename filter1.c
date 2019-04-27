/******************************* SOURCE LICENSE *********************************
Copyright (c) 2019 MicroModeler.

A non-exclusive, nontransferable, perpetual, royalty-free license is granted to the Licensee to 
use the following Information for academic, non-profit, or government-sponsored research purposes.
Use of the following Information under this License is restricted to NON-COMMERCIAL PURPOSES ONLY.
Commercial use of the following Information requires a separately executed written license agreement.

This Information is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

******************************* END OF LICENSE *********************************/

// A commercial license for MicroModeler DSP can be obtained at http://www.micromodeler.com/launch.jsp

#include "filter1.h"

#include <stdlib.h> // For malloc/free
#include <string.h> // For memset

float filter1_coefficients[24] = 
{
	0.0000000, 0.0000000, 0.0000000, -0.0065789546, -0.018644475, 0.0026805838,
	-0.025078450, -0.0077836133, 0.085685335, 0.082781572, -0.11728755, -0.19576730,
	0.056277211, 0.25256022, 0.056277211, -0.19576730, -0.11728755, 0.082781572,
	0.085685335, -0.0077836133, -0.025078450, 0.0026805838, -0.018644475, -0.0065789546
};


filter1Type *filter1_create( void )
{
	filter1Type *result = (filter1Type *)malloc( sizeof( filter1Type ) );	// Allocate memory for the object
	filter1_init( result );											// Initialize it
	return result;																// Return the result
}

void filter1_destroy( filter1Type *pObject )
{
	free( pObject );
}

 void filter1_init( filter1Type * pThis )
{
	filter1_reset( pThis );

}

 void filter1_reset( filter1Type * pThis )
{
	memset( &pThis->state, 0, sizeof( pThis->state ) ); // Reset state to 0
	pThis->pointer = pThis->state;						// History buffer points to start of state buffer
	pThis->output = 0;									// Reset output

}

 int filter1_filterBlock( filter1Type * pThis, float * pInput, float * pOutput, unsigned int count )
{
	float *pOriginalOutput = pOutput;	// Save original output so we can track the number of samples processed
	float accumulator;
 
 	for( ;count; --count )
 	{
 		pThis->pointer[filter1_length] = *pInput;						// Copy sample to top of history buffer
 		*(pThis->pointer++) = *(pInput++);										// Copy sample to bottom of history buffer

		if( pThis->pointer >= pThis->state + filter1_length )				// Handle wrap-around
			pThis->pointer -= filter1_length;
		
		accumulator = 0;
		filter1_dotProduct( pThis->pointer, filter1_coefficients, &accumulator, filter1_length );
		*(pOutput++) = accumulator;	// Store the result
 	}
 
	return pOutput - pOriginalOutput;

}

 void filter1_dotProduct( float * pInput, float * pKernel, float * pAccumulator, short count )
{
 	float accumulator = *pAccumulator;
	while( count-- )
		accumulator += ((float)*(pKernel++)) * *(pInput++);
	*pAccumulator = accumulator;

}


