/**
 * Script wrapper para executar criaEEnviaTransacaoSendMainnet via CLI
 * Uso: npx tsx exec-transacao.ts <chave_privada> <carteira_destino> <valor_minimo> <valor_sol>
 */

import { criaEEnviaTransacaoSendMainnet } from './cria-transacao-send-post-mainnet';

async function main() {
  try {
    // Ler argumentos da linha de comando
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
      throw new Error('Uso: npx tsx exec-transacao.ts <chave_privada> <carteira_destino> <valor_minimo> [valor_sol]');
    }
    
    const chavePrivada = args[0];
    const carteiraDestino = args[1];
    const valorMinimo = args[2] === 'true';
    const valorSOL = args[3] ? parseFloat(args[3]) : undefined;
    
    // Validar parâmetros
    if (!chavePrivada || !carteiraDestino) {
      throw new Error('chave_privada e carteira_destino são obrigatórios');
    }
    
    // Executar a função
    const signature = await criaEEnviaTransacaoSendMainnet(
      chavePrivada,
      carteiraDestino,
      valorMinimo,
      valorSOL
    );
    
    // Retornar resultado em JSON via stdout
    console.log(JSON.stringify({
      sucesso: true,
      signature: signature
    }));
    
    process.exit(0);
  } catch (error: any) {
    // Retornar erro em JSON via stderr
    const errorObj = {
      sucesso: false,
      erro: error.message || String(error)
    };
    console.error(JSON.stringify(errorObj));
    process.exit(1);
  }
}

main();
