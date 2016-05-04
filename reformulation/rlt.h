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

#ifndef RLT_H
#define RLT_H

template< typename Func >
void printObjective( const Matrix& probabilities, const Matrix& distances, double eps, Func f ) {
  assert( probabilities.size() == distances.size() );
  const unsigned int n = probabilities.size();
  for( unsigned int k = 0; k < n; ++k ) {
    for( unsigned int i = 0; i < n; ++i ) {
      for( unsigned int l = 0; l < n; ++l ) {
        for( unsigned int j = 0; j < n; ++j ) {
          if( k==l && i==j ) {
            const double cost = probabilities[k][k]*distances[i][i];
            if( fabs( cost ) >= eps ) {
              std::cout << " + " << cost << " " << name("x",k,i) << std::endl;
            }
          } else if( (i==j) && (k!=l) ) {
          } else if( (k==l) && (i!=j) ) {
          } else {
            const double cost = 0.5*( probabilities[k][l]*distances[i][j] + probabilities[l][k]*distances[j][i] );
            if( fabs( cost ) >= eps ) {
              std::cout << " + " << cost << " " << f(k,i,l,j) << std::endl;
            }
          }
        }
      }
    }
  }
}

void printRLT1( int n ) {
  for( int k = 0; k < n; ++k ) {
    for( int i = 0; i < n; ++i ) {
      for( int l = 0; l < n; ++l ) {
        if( k==l ) continue;
        for( int j = 0; j < n; ++j ) {
          if( i==j ) continue;
          std::cout << " + " << name("y",l,j,k,i) << std::endl;
        }
        std::cout << " - " << name("x",k,i) << " = 0" << std::endl;
      }
    }
  }
  for( int k = 0; k < n; ++k ) {
    for( int i = 0; i < n; ++i ) {
      for( int j = 0; j < n; ++j ) {
        if( i==j ) continue;
        for( int l = 0; l < n; ++l ) {
          if( k==l ) continue;
          std::cout << " + " << name("y",l,j,k,i) << std::endl;
        }
        std::cout << " - " << name("x",k,i) << " = 0" << std::endl;
      }
    }
  }
}

void printSQAP( int n ) {
  for( int k = 0; k < n; ++k ) {
    for( int l = 0; l < k; ++l ) {
      for( int i = 0; i < n; ++i ) {
        for( int j = 0; j < i; ++j ) {
          std::cout << " + " << name("y",l,j,k,i) << std::endl;
        }
        for( int j = i+1; j < n; ++j ) {
          std::cout << " + " << name("y",l,i,k,j) << std::endl;
        }
        std::cout << " - " << name("x",l,i) << " - " << name("x",k,i) << " = 0" << std::endl;
      }
    }
  }
  for( int j = 0; j < n-3; ++j ) {
    for( int i = j+1; i < n-1; ++i ) {
      for( int k = 0; k < n; ++k ) {
        for( int l = 0; l < k; ++l ) {
          std::cout << " + " << name("y",l,j,k,i) << std::endl;
        }
        for( int l = k+1; l < n; ++l ) {
          std::cout << " + " << name("y",k,j,l,i) << std::endl;
        }
        std::cout << " - " << name("x",k,j) << " - " << name("x",k,i) << " = 0" << std::endl;
      }
    }
  }
}

#endif