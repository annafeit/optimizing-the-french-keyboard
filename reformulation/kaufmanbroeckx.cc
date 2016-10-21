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
  // transfer first line of comments to new file
  //cin >> firstcomment;
  //cout << firstcomment;
  ignoreComment();
  
  unsigned int nn;
  ignoreComment();
  cin >> nn;
  const unsigned int n = nn;
  
  Matrix probabilities = emptyMatrix( n );
  Matrix distances = emptyMatrix( n );
  Matrix linearcosts = emptyMatrix( n );
  
  ignoreComment();
  readMatrix( probabilities );
  ignoreComment();
  readMatrix( distances );
  
  ignoreComment();
  auto fixations = readFixations();
  
  ignoreComment();
  scale( probabilities );
  
  ignoreComment();
  if((std::cin >> std::ws ).peek())
     readMatrix( linearcosts);

  cout << "minimize" << endl;
  printKaufmanBroeckxObjective( n );
  
  cout << "subject to" << endl;
  printAssignment( n );

  printKaufmanBroeckxInequalities( probabilities, distances, linearcosts, 1e-8 );
    
  printFixations( fixations );
  
  cout << "binaries" << endl;
  printX( n );
  
  cout << "end" << endl;
  
  return 0;
}
