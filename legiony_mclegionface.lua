require "pdf"
p = PDF.new()
times = p:new_font{name="Times-Roman"}
page = p:new_page()
page:begin_text()
page:set_font(times, 12)
page:set_text_pos(100, 100)
for i = 1, 10000 do
    page:set_text_pos(0, 0)
    page:show("Bro, do you even contain multitudes?")
end
page:end_text()
page:add()
p:write("Legiony_McLegionface.txt")
