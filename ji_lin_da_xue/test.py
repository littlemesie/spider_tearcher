a = "ad28eb096d20a05a8ad89ac44039baa2958036bfc1a859c436c0def6da6632ef77f07fe120d31d87eb9fc55990a3a2939493c2438f2c94ad9a9d4c20c2d464c640b82bedd9a504dd52033d0d565d1c5fcf03fa9cfa7bb074c11940a1f9246e45d729f0af9b75ac97c19343196c516997cbbc2997ea2afcfd6986f5247e7608b9"

print(len(a))

b = a.replace("/[^A-Za-z0-9\+\/\=]/g", "")
print(b)


from base64 import decodestring

c = decodestring(a)
print(c)