const fipe = require('fipe-promise');
const fs = require('fs');
const marcaAlvo = { codigo: '238', nome: 'BYD' };

async function coletarDadosBYD() {
    try {
        const modelos = await fipe.fetchModels(fipe.vehicleType.CARS, marcaAlvo.codigo);
        console.log(`Encontrados ${modelos.length} modelos.`);

        const todosOsVeiculosBYD = [];

        for (const modelo of modelos) {
            const anos = await fipe.fetchYears(fipe.vehicleType.CARS, marcaAlvo.codigo, modelo.codigo);

            for (const ano of anos) {

                try {
                    console.log(`  -> Coletando dados para o ano: ${ano.nome}`);
                    const ficha = await fipe.fetchDetail(fipe.vehicleType.CARS, marcaAlvo.codigo, modelo.codigo, ano.codigo);

                    todosOsVeiculosBYD.push(ficha);

                } catch (err) {
                    console.error(`      Erro ao buscar ficha para ${modelo.nome} ${ano.nome}:`, err.message);
                }
            }
        }
        return todosOsVeiculosBYD;

    } catch (err) {
        console.error("Ocorreu um erro geral no processo:", err);
        return null;
    }
}

coletarDadosBYD().then(dadosColetados => {
    if (dadosColetados && dadosColetados.length > 0) {
        const nomeArquivo = 'dataset_byd_fipe.json';
        fs.writeFileSync(nomeArquivo, JSON.stringify(dadosColetados, null, 2), 'utf8');

        console.log(`\n\nProcesso finalizado!`);
        console.log(`Os dados da BYD foram salvos no arquivo '${nomeArquivo}'.`);
        console.log(`Total de ${dadosColetados.length} veículos/versões coletados.`);
    } else {
        console.log("\nNenhum dado foi coletado. Verifique os erros no console.");
    }
});