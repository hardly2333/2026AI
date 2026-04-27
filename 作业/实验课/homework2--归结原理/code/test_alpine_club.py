import Convert_input as ci
from slover import solve, format_clause


def test_alpine_club():

    alpine_kb = [
    "A(tony)",                             
    "A(mike)",                             
    "A(john)",                             
    "L(tony,rain)",                        
    "L(tony,snow)",                       
    "(~A(x), S(x), C(x))",              
    "(~C(y), ~L(y,rain))",            
    "(L(z,snow), ~S(z))",               
    "(~L(tony,u), ~L(mike,u))",      
    "(L(tony,v), L(mike,v))",          
    "(~A(w), ~C(w), S(w))"              
    ]
    
    import Convert_input as ci
    from slover import solve 
    
    kb_list = [ci.parse_clause(c) for c in alpine_kb]
    
    print("--- 正在解决 Alpine Club 问题 ---")
    success = solve(kb_list)
    if success:
        print("\nSuccess!")
    else:
        print("\nFail.")

if __name__ == "__main__":
    test_alpine_club()