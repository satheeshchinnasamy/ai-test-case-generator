class TestCase:

    def __init__(self,id, title, type="positive"):
        self.id=id
        self.title=title
        self.type=type
        
    def display(self):
        print(f"{self.id}-{self.title} ({self.type})")

    def to_dict(self):
        return{
            "id":self.id,
            "title":self.title,
            "type":self.type
        }
    
tc1=TestCase("TC_001", "Valid Login")
tc2=TestCase("TC_002", "Invalid Login", type="Negative")

tc1.display()
tc2.display()
print(tc1.to_dict())