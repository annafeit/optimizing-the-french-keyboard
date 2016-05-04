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

#ifndef ASSIGNMENT_H
#define ASSIGNMENT_H

#include "utils.h"

void printX( int n ) {
  for( int k = 0; k < n; ++k ) {
    for( int i = 0; i < n; ++i ) {
      std::cout << name("x",k,i) << " ";
    }
    std::cout << std::endl;
  }
}

void printAssignment( int n ) {
  for( int k = 0; k < n; ++k ) {
    for( int i = 0; i < n; ++i ) {
      std::cout << " + " << name("x",k,i);
    }
    std::cout << " = 1" << std::endl;
  }
  for( int i = 0; i < n; ++i ) {
    for( int k = 0; k < n; ++k ) {
      std::cout << " + " << name("x",k,i);
    }
    std::cout << " = 1" << std::endl;
  }
}

#endif