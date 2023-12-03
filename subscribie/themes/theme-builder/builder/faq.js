const colSm12 = document.querySelectorAll(".col-sm-12");

colSm12.forEach((item, index) => {
  let header = item.querySelector("header");
  header.addEventListener("click", () =>{
    item.classList.toggle("open");

    let description = item.querySelector(".description");
      if(item.classList.contains(open)){
        description.style.height = `${description.scrollHeight}px`;//scrollHeight property returns the height of an element including padding, but excluding borders, scrollbar or margin
        item.querySelector("i").classList.replace("fa-plus", "fa-minus");
      }else{
        description.style.height = "0px";
        item.querySelector("i").classList.replace("fa-minus", "fa-plus");
      }
      removeOpen(index); //calling the function and also passing the index number of the clicked header
  })
  
})

function removeOpen(index){
  colSm12.forEach((item2, index2) => {
    if(index1 != index2){
      item2.classList.remove("open");

      let description = item2.querySelector(".description");
      description.style.height = "0px";
      item2.querySelector("i").classList.replace("fa-minus", "fa-plus");
    }
  })
}