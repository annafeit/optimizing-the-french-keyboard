/******************************************************************************* 
 * Copyright (c) 2014, Andreas Karrenbauer
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * The name of the author may not be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
 * EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
 *******************************************************************************/

#ifndef KAUFMANBROECKX_H
#define KAUFMANBROECKX_H

#include "utils.h"

void printKaufmanBroeckxInequalities( const Matrix& probabilities, const Matrix& distances, const Matrix& similarities, double eps ) {
  assert( probabilities.size() == distances.size() );
  assert( probabilities.size() == similarities.size() );
  const unsigned int n = probabilities.size();
  
  Matrix c = emptyMatrix( n );
  for( unsigned int k = 0; k < n; ++k ) {
    for( unsigned int i = 0; i < n; ++i ) {
      for( unsigned int l = 0; l < n; ++l ) {
        for( unsigned int j = 0; j < n; ++j ) {
          c[k][i] += probabilities[k][l]*distances[i][j]*similarities[k][l];
        }
      }
    }
  }
  
  for( unsigned int k = 0; k < n; ++k ) {
    for( unsigned int i = 0; i < n; ++i ) {
      std::cout << c[k][i] << " " << name( "x", k, i );
      for( unsigned int l = 0; l < n; ++l ) {
        for( unsigned int j = 0; j < n; ++j ) {
          const double pd = probabilities[k][l]*distances[i][j]*similarities[k][l];
          if( pd > eps ) {
            std::cout << " + " << pd << " " << name( "x",l,j ) << std::endl; 
          }
        }
      }
      std::cout << " - " << name( "w",k,i ) << " <= " << c[k][i] << std::endl;
    }
  }     
}

void printKaufmanBroeckxObjective( unsigned int n ) {
  for( unsigned int k = 0; k < n; ++k ) {
    for( unsigned int i = 0; i < n; ++i ) {
      std::cout << " + " << name( "w",k,i );
    }
    std::cout << std::endl;
  }
}

#endif
