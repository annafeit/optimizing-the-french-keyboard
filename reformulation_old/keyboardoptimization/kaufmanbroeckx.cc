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

#include "utils.h"
#include "assignment.h"
#include "kaufmanbroeckx.h"

using namespace std;

int main() {
  
  unsigned int nn;
  ignoreComment();
  cin >> nn;
  const unsigned int n = nn;
  
  Matrix probabilities_letter = emptyMatrix( n );
  Matrix probabilities_bigram = emptyMatrix( n );
  Matrix performance = emptyMatrix( n );
  Matrix distances_0 = emptyMatrix( n );
  Matrix distances_1 = emptyMatrix( n );
  Matrix similarities = emptyMatrix( n );
  Matrix distances_azerty = emptyMatrix( n );
  Matrix ergonomics = emptyMatrix( n );
  
  ignoreComment();
  readMatrix( probabilities_letter );
  ignoreComment();
  readMatrix( probabilities_bigram );
  ignoreComment();
  readMatrix( performance );
  ignoreComment();
  readMatrix( distances_0 );  
  ignoreComment();
  readMatrix( distances_1 );    
  ignoreComment();
  readMatrix( similarities );
  ignoreComment();
  readMatrix( distances_azerty );
  ignoreComment();
  readMatrix( ergonomics );
  
  ignoreComment();
  auto weights = readWeights();
  
  ignoreComment();
  auto fixations = readFixations();
  
  ignoreComment();
  scale( probabilities );
  
  cout << "minimize" << endl;
  printKaufmanBroeckxObjective( n );
  
  cout << "subject to" << endl;
  printAssignment( n );

  printKaufmanBroeckxInequalities( probabilities, distances, similarities, 1e-8 );
    
  printFixations( fixations );
  
  cout << "binaries" << endl;
  printX( n );
  
  cout << "end" << endl;
  
  return 0;
}