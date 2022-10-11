import Data.Array

tabulate :: Ix i => (i -> e) -> (i, i) -> Array i e
tabulate f bounds = array bounds [(x, f x) | x <- range bounds]

badFib :: Int -> Int
badFib n = if n <= 1 then 1 else badFib (n -1) + badFib (n -2)

tdFib :: Int -> Int
tdFib n = a ! n
  where a = tabulate f (0, n)
        f i = if i <= 1 
              then fromIntegral i 
              else a ! (i - 1) + a ! (i - 2)

buFib :: Int -> Int
buFib n = fst (apply n step (0, 1))
  where step (a, b) = (b, a + b)
        apply n f x = if n == 0 
                      then x 
                      else apply (n - 1) f (f x)

funFib = 1 : 1 : zipWith (+) funFib (tail funFib)

