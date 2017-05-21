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

predicate sorted (a:array<int>, start:int, end:int)
 requires a!=null
 requires 0<=start<=end<=a.Length
 reads a
{
 forall j,k:: start <= j < k < end ==> a[j]<=a[k]
}

method Bubble_sort(a: array<int>)
requires a != null && a.Length > 1;
modifies a;
ensures sorted(a, 0, a.Length);
{
  var i := 0;
  while (i < a.Length) 
    invariant 0 <= i <= a.Length
    invariant sorted(a, a.Length - i, a.Length)
    invariant forall k :: 0 <= k < a.Length - i && i > 0 ==> a[k] <= a[a.Length -i]
    decreases a.Length - i
  {
    var j := 0;
    while (j < a.Length - i - 1) 
      invariant 0 <= j <= a.Length - i - 1
      invariant sorted(a, a.Length - i, a.Length)  
      invariant forall k :: 0 <= k < a.Length - i && i > 0 ==> a[k] <= a[a.Length -i]
      invariant forall k :: 0 <= k < j ==> a[k] <= a[j]
      invariant i > 0 ==> a[j] <= a[a.Length - i]
      decreases a.Length - i - 1 - j
    {
      if a[j] > a[j+1]
      {
        var temp := a[j];
        a[j] := a[j+1];
        a[j+1] := temp;
      }
      
      j := j + 1;
    }
    
    i := i + 1;
  }
}