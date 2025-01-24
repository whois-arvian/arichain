const { prompt, logMessage, rl } = require("./utils/logger");
const ariChain = require("./classes/ariChain");
const { generateRandomPassword } = require("./utils/generator");
const { getRandomProxy, loadProxies } = require("./classes/proxy");

const chalk = require("chalk");
const fs = require("fs");

async function main() {
  console.log(
    chalk.cyan(`
░█▀█░█▀▄░▀█▀░█▀▀░█░█░█▀█░▀█▀░█▀█
░█▀█░█▀▄░░█░░█░░░█▀█░█▀█░░█░░█░█
░▀░▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀
     By : El Puqus Airdrop
     github.com/ahlulmukh
  `)
  );

  const captchaSolverResponse = await prompt(
    chalk.yellow(
      "Choose CAPTCHA solver (1 for 2Captcha, 2 for Anti-Captcha, 3 for Gemini): "
    )
  );
  const use2Captcha = captchaSolverResponse === "1";
  const useAntiCaptcha = captchaSolverResponse === "2";
  const useGemini = captchaSolverResponse === "3";
  const refCode = await prompt(chalk.yellow("Enter Referral Code: "));
  const toAddress = await prompt(
    chalk.yellow("Enter target address for token transfer: ")
  );
  const count = parseInt(await prompt(chalk.yellow("How many do you want? ")));
  const proxiesLoaded = loadProxies();
  if (!proxiesLoaded) {
    console.log(chalk.yellow("No proxy available. Using default IP."));
  }
  let successful = 0;

  const accountAri = fs.createWriteStream("accounts.txt", { flags: "a" });

  for (let i = 0; i < count; i++) {
    console.log(chalk.white("-".repeat(85)));
    logMessage(i + 1, count, "Process", "debug");

    const currentProxy = await getRandomProxy();
    const generator = new ariChain(refCode, currentProxy);

    try {
      const email = generator.generateTempEmail();
      const password = generateRandomPassword();

      const emailSent = await generator.sendEmailCode(
        email,
        use2Captcha,
        useAntiCaptcha
      );
      if (!emailSent) continue;

      const account = await generator.registerAccount(email, password);

      if (account) {
        accountAri.write(`Email: ${email}\n`);
        accountAri.write(`Password: ${password}\n`);
        accountAri.write(`Reff To: ${refCode}\n`);
        accountAri.write("-".repeat(85) + "\n");

        successful++;
        logMessage(i + 1, count, "Account Success Create!", "success");
        logMessage(i + 1, count, `Email: ${email}`, "success");
        logMessage(i + 1, count, `Password: ${password}`, "success");
        logMessage(i + 1, count, `Reff To : ${refCode}`, "success");

        const address = account.result.address;
        try {
          const checkinResult = await generator.checkinDaily(address);
          logMessage(i + 1, count, `Checkin Daily Done`, "success");
          if (!checkinResult) {
            throw new Error("Gagal checkin");
          }
          const transferResult = await generator.transferToken(
            email,
            toAddress,
            password,
            60
          );
          if (!transferResult) {
            throw new Error("Gagal transfer token");
          }
          logMessage(i + 1, count, `Transfer Token Done`, "success");
        } catch (error) {
          logMessage(i + 1, count, error.message, "error");
          continue;
        }
      } else {
        logMessage(i + 1, count, "Register Account Failed", "error");
        if (generator.proxy) {
          logMessage(i + 1, count, `Failed proxy: ${generator.proxy}`, "error");
        }
      }
    } catch (error) {
      logMessage(i + 1, count, `Error: ${error.message}`, "error");
    }
  }

  accountAri.end();

  console.log(chalk.magenta("\n[*] Dono bang!"));
  console.log(chalk.green(`[*] Account dono ${successful} dari ${count} akun`));
  console.log(chalk.magenta("[*] Result in accounts.txt"));
  rl.close();
}

module.exports = { main };
