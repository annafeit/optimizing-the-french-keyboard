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

#ifndef UTILS_H
#define UTILS_H

#include <iostream>
#include <vector>
#include <sstream>
#include <math.h>
#include <assert.h>
#include <limits>

int bits( int n ) {
  int w = 1;
  while( n > (1<<w) ) {
    ++w;
  }
  return w;
}

std::string name( const std::string& prefix, int l, int j ) {
  std::stringstream ss;
  ss << prefix << "(" << l << "," << j << ")";
  return ss.str();
}

std::string name( const std::string& prefix, int k, int i, int l, int j ) {
  std::stringstream ss;
  if( l < k ) {
    ss << prefix << "(" << k << "," << i << "," << l << "," << j << ")";
  } else {
    ss << prefix << "(" << l << "," << j << "," << k << "," << i << ")";
  }     
  return ss.str();
}

typedef std::vector< std::vector<double> > Matrix;

Matrix emptyMatrix( int n ) {
  return Matrix( n, std::vector<double>( n ) );
}

void readMatrix( Matrix& M ) {
  for( auto& r : M ) {
    for( auto& a : r ) {
      std::cin >> a;
    }
  }
}

template< typename T >
void readVector( std::vector<T>& v ) {
  for( auto& a : v ) {
    std::cin >> a;
  }
}

void transpose( const Matrix& M, Matrix& T ) {
  unsigned int n = M.size();
  for( unsigned int i = 0; i < n; ++i ) {
    for( unsigned int j = 0; j < n; ++j ) {
      T[j][i] = M[i][j];
    }
  }
}

std::vector<int> binarydecomposition( int i, int w ) {
  std::vector<int> ret( w );
  for( int b = 0; b < w; ++b ) {
    const int j = i >> b;
    ret[b] = j%2;
  }
  return ret;
}

struct LetterSlot {
  unsigned int letter;
  unsigned int slot;
};

std::vector<LetterSlot> readFixations() {
  unsigned int ff;
  std::cin >> ff;
  const unsigned int f = ff;
   
  std::vector<LetterSlot> F;
  for( unsigned int i = 0; i < f; ++i ) {
    unsigned int l,j;
    std::cin >> l;
    std::cin >> j;
    F.push_back( {l,j} );
  }
  return F;
}

void printFixations( const std::vector<LetterSlot>& F ) {
  for( auto f : F ) {
    std::cout << name( "x", f.letter, f.slot ) << " = 1" << std::endl;
  }
}

void scale( Matrix& M ) {
  double scale;
  std::cin >> scale;
  
  const unsigned int n = M.size();
  
  for( unsigned int l = 0; l < n; ++l ) {
    for( unsigned int k = 0; k < n; ++k ) {
      M[l][k] = floor( M[l][k]*scale )/scale;
    }
  }
}

void ignoreComment() {
  if( (std::cin >> std::ws ).peek() == std::char_traits<char>::to_int_type('#') ) {
    std::cin.ignore( std::numeric_limits<std::streamsize>::max(), '\n' );
  }
}

#endif
