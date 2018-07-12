$(document).ready(() => {
    console.log("Hello, world !");
    function loadAllTaxons(data) {
        for (let i = 0; i < data.length; i++) {
            console.log(data[i]);
            $('#prevTaxSelect').append(`<option value="${i}">${data[i].fields.taxon} - ${data[i].fields.genre} ${data[i].fields.espece}</option>`);
        }
        console.log('done');
    }
    loadAllTaxons(tax);
    $('.chosen-select').chosen({
        width: '50%'
    });

    function getNextTaxon(tax_ind, data) {
        for (let i = tax_ind; i < data.length - 1; i++) {
            if (data[i].fields.taxon < data[i+1].fields.taxon) {
                return i+1;
            }
        }

        return tax_ind;
    }
    function getNewTaxon(current, next) {
        if (current == next) {
            return current + 100;
        }
        let add_list = [100, 50, 25, 10, 5, 1];
        for (let k = 0; k < add_list.length; k++) {
            if (current + add_list[k] < next) {
                return current + add_list[k];
            }
        }
        return current + 1;
    }

    $('#taxBtn').on('click', (e) => {
        e.preventDefault();
        let choice = parseInt($('#prevTaxSelect').val(),10);
        let next = getNextTaxon(choice, tax);
        let suiv = getNewTaxon(tax[choice].fields.taxon, tax[next].fields.taxon);
        $("#id_taxon").val(suiv);
        $('#taxonModal').modal('hide');
    });
});
