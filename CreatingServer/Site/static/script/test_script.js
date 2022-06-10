function Enter() {

    

    // let req = new Object();
    let arr = new Array();

    let answers = document.getElementById('answers').getElementsByTagName('div'); 
    
    id = document.getElementById("get_id").value

    count = 0
    is_not_all_answers = false
    for (let i = 0; i < answers.length; i++) {
        // console.log(document.getElementById(`answer-${i}`).checked) 

        let input_content = answers[i].getElementsByTagName('input')
        for (let j = 0; j < input_content.length; j++) {
            

            if (input_content[j].checked){
                count += 1
                arr.push(j)
            }
        }
        if (count == 0){
            is_not_all_answers = true
            break
        } 
        count = 0 
    }
    console.log(arr)

    if (!is_not_all_answers){
        
        let resultModal = document.getElementById('resultModal');
        resultModal.style.display = 'flex';


        let url = new URL(window.location.origin + `/api/answer/${id}`)
        let request = {
            data: arr
        }
        console.log(JSON.stringify(request))
        // console.log(window.location.origin)
        // console.log(url)
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' //Mime-type 
            },
            body: JSON.stringify(request)
        }).then(response => {
            if (response.ok)
                return response.json();
            else
                alert("произощла ошибка");
        }).then((data)=> {
            let modalContent = document.getElementById('modalContent');
            modalContent.innerText = "Процент правильных ответов: " + JSON.stringify(data.result)+"%";
        }); 
    }
    else{
        alert("Выберите в каждом вопросе по ответу.")
    }
}