# -*- coding:utf-8 -*-
# Date   : Fri Nov 09 12:42:05 2018 +0800
# Author : Rory Xiang

import execjs


a = """
        function (input) {   
        var output=new Array();
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;   
        var i = 0;   
        input = _utf8_encode(input);   
        
        while (i < input.length) 
        {   
            chr1 = input[i++];
            chr2 = input[i++];
            chr3 = input[i++];
    
            enc1 = chr1 >> 2;   
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);   
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);   
            enc4 = chr3 & 63;   
            if (isNaN(chr2)) {   
                enc3 = enc4 = 64;   
            } else if (isNaN(chr3)) {   
                enc4 = 64;   
            }   
            output.push(_keyStr.charAt(enc1) + _keyStr.charAt(enc2) + _keyStr.charAt(enc3) + _keyStr.charAt(enc4));   
        }   
        return output.join('');
    }
"""
b = """05f7e0cbc40bbca287f0a7bb7dd2b29b9951eef91858d6f711f422ef1333a7007838914853b29e7ccb75761c9925533e3747d0cf112ced7b40ca4d140e337703b9ac10e12a652776fac9a9ebce1450b3b9e6a51f19f06e476fc4f7f4c0bc9e8cb1c96dd9c972562b7f9f7d79c1346440dcee5586efc727d801f224e4d9958b1b"""
fun = execjs.compile(a)
print(fun)
ll = fun.call(b)
print(ll)