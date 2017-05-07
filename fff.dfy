// n = number of elements to be summed
function sum(a: array<int>, n: int): int
  requires a != null;
  requires n <= a.Length;
  decreases n;
  reads a;
{
  if (n <= 0) then 0 else a[n-1] + sum(a, n-1)
}

method average(a: array<int>) returns (avg: int)
  requires a != null;
  ensures if a.Length == 0 then avg == -1 else avg == sum(a, a.Length)/a.Length;
{
  var total:int := 0;
  var i:int := 0;
  
  while (0 <= i < a.Length) 
    invariant 0 <= i <= a.Length;
    invariant total == sum(a, i);
    decreases a.Length - i;
  {
    total := total + a[i];
    i := i + 1;
  }
  
  if (i == 0) {avg := -1;} else {avg := total/i;}
}