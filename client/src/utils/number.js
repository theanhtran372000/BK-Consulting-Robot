export const roundNumber = (number, digits=0) => Math.round(number * (10 ** digits)) / (10 ** digits)

export const listAverage = (arr) => arr.reduce((acc, curr) => acc + curr, 0) / arr.length;

export const listMedian = (arr) => {
  arr.sort((a, b) => a - b);
  
  const middle = Math.floor(arr.length / 2);
  const median = arr[middle];
  
  if (arr.length % 2 === 0)
      return median;
  
  return (median + arr[middle + 1]) / 2
}

export const listSum = (arr) => arr.reduce((acc, curr) => acc + curr, 0)