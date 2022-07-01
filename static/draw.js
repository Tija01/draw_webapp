var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
// Default style
setCanvasBgColor(canvas, 'white');
ctx.fillStyle = "black";


function setCanvasBgColor(canvas, color) 
{
    // Its good practice to save a context state that will be modified
    ctx.save();

    // To keep the existing drawing as the bg color is changed
    ctx.globalCompositeOperation = 'destination-over';
    
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.restore();
}


function resize(event)
{
    var select = document.getElementById('size');
    var option = select.options[select.selectedIndex];           

    if (option.value == "small")
    {                
        canvas.width = 200;
        canvas.height = 100;
    }
    
    if (option.value == "medium")
    {
        canvas.width = 800;
        canvas.height = 400;
    }

    if (option.value == "A4")
    { 
        canvas.width = 3508;
        canvas.height = 2480;
    }
    setCanvasBgColor(canvas, 'white');
}

function customize(event)
{
    // Change canvas color
    var bgcolor = document.getElementById("bg-color").value;
    ctx.fillStyle = bgcolor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Change fill color
    var fill_color = document.getElementById("fill-color").value;
    ctx.fillStyle = fill_color;

    // Change stroke color
    var stroke_color = document.getElementById('stroke-color').value;
    ctx.strokeStyle = stroke_color;

    // Change stroke width
    var stroke_width = document.getElementById('stroke-width').value
    ctx.lineWidth = stroke_width;  
}


function line(event)
{
    var x1 = document.getElementById('x1').value;
    var y1 = document.getElementById('y1').value;
    var x2 = document.getElementById('x2').value;
    var y2 = document.getElementById('y2').value;
    ctx.moveTo(x1/100*canvas.width, y1/100*canvas.height);
    ctx.lineTo(x2/100*canvas.width, y2/100*canvas.height);
    ctx.stroke();
}

function rect(event)
{
    var x1 = document.getElementById('x1_rect').value;
    var y1 = document.getElementById('y1_rect').value;
    var x2 = document.getElementById('x2_rect').value;
    var y2 = document.getElementById('y2_rect').value;

    if(document.getElementById('fill_rect').checked) 
        {
            ctx.fillRect(x1/100*canvas.width, y1/100*canvas.height, x2/100*canvas.width, y2/100*canvas.height)
            ctx.stroke();
        }
    else
    {
        ctx.beginPath();            
        ctx.rect(x1/100*canvas.width, y1/100*canvas.height, x2/100*canvas.width, y2/100*canvas.height);
        ctx.stroke();
    }
}


function arc(event)
{
    var x = document.getElementById('x_arc').value / 100 * canvas.width;
    var y = document.getElementById('y_arc').value / 100 * canvas.height;
    var r = document.getElementById('r_arc').value / 100 * canvas.width;
    var ang_start = document.getElementById('ang_start').value / 360 * 2 * Math.PI;
    var ang_end = document.getElementById('ang_end').value / 360 * 2 * Math.PI;
    var counter_clock = document.getElementById('counter_clock').checked

    ctx.beginPath();
    ctx.arc(x, y, r, ang_start, ang_end, counter_clock);
    ctx.stroke();
}


function save(event)
{
    //Convert the canvas to blob and post the file
    canvas.toBlob(postFile, 'image/jpeg');
    
    //Add file blob to a form and post
    function postFile(file) {
        if (confirm("The drawing will be saved to your homepage and the public library"))
        {
        let formdata = new FormData();
        formdata.append("image", file);
        let xhr = new XMLHttpRequest();
        xhr.open('POST', 'http://127.0.0.1:5000/image', true);
        xhr.onload = function () {
        if (this.status === 200)
            console.log(this.response);
        else
            console.error(xhr);
        };
        xhr.send(formdata);
        }
    }
}